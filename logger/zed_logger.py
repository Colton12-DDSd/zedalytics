import asyncio
import websockets
import json
import uuid
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from config import WS_URL, BEARER_TOKEN, SUPABASE_DB_URL


# === DB Engine ===
engine = create_async_engine(SUPABASE_DB_URL, echo=False)

# === DB Insert/Upsert Functions ===
async def upsert_horse(horse):
    query = text("""
        INSERT INTO horses (id, name, bloodline, generation, gender, rating, speed_rating, sprint_rating, endurance_rating, state)
        VALUES (:id, :name, :bloodline, :generation, :gender, :rating, :speed_rating, :sprint_rating, :endurance_rating, :state)
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            bloodline = EXCLUDED.bloodline,
            generation = EXCLUDED.generation,
            gender = EXCLUDED.gender,
            rating = EXCLUDED.rating,
            speed_rating = EXCLUDED.speed_rating,
            sprint_rating = EXCLUDED.sprint_rating,
            endurance_rating = EXCLUDED.endurance_rating,
            state = EXCLUDED.state;
    """)
    async with engine.begin() as conn:
        await conn.execute(query, horse)

async def upsert_stable(stable):
    query = text("""
        INSERT INTO stables (user_id, stable_name)
        VALUES (:user_id, :stable_name)
        ON CONFLICT (user_id) DO UPDATE SET
            stable_name = EXCLUDED.stable_name;
    """)
    async with engine.begin() as conn:
        await conn.execute(query, stable)

async def insert_race_and_participants(race, participants):
    async with engine.begin() as conn:
        await conn.execute(text("""
            INSERT INTO races (id, name, start_time, pots_total)
            VALUES (:id, :name, :start_time, :pots_total)
            ON CONFLICT DO NOTHING;
        """), {
            "id": race["id"],
            "name": race["name"],
            "start_time": race["startTime"],
            "pots_total": race.get("racePotsTotal", 0)
        })

        for p in participants:
            await conn.execute(text("""
                INSERT INTO race_participants (
                    id, race_id, horse_id, user_id, gate_number, finish_position,
                    finish_time, earnings, stake, odds,
                    starting_points, ending_points, points_change,
                    cpu_augment, ram_augment, hydraulic_augment,
                    cpu_augment_triggered, ram_augment_triggered, hydraulic_augment_triggered,
                    sectional_positions
                ) VALUES (
                    :id, :race_id, :horse_id, :user_id, :gate_number, :finish_position,
                    :finish_time, :earnings, :stake, :odds,
                    :starting_points, :ending_points, :points_change,
                    :cpu_augment, :ram_augment, :hydraulic_augment,
                    :cpu_triggered, :ram_triggered, :hydraulic_triggered,
                    :sectional_positions
                );
            """), p)

# === WEBSOCKET CONNECTION ===
async def main():
    async with websockets.connect(WS_URL, subprotocols=["graphql-transport-ws"]) as ws:
        await ws.send(json.dumps({
            "type": "connection_init",
            "payload": {"authorization": BEARER_TOKEN}
        }))
        await ws.recv()

        op_id = str(uuid.uuid4())
        await ws.send(json.dumps({
            "id": op_id,
            "type": "subscribe",
            "payload": {
                "operationName": "RaceEventSub",
                "query": """
                subscription RaceEventSub($where: SimpleEntityEventWhereInput) {
                  raceEvent(where: $where) {
                    id
                    timestamp
                    action
                    entityId
                    entityTypename
                    entity {
                      ... on Race {
                        id
                        name
                        status
                        startTime
                        finishTime
                        racePotsTotal
                        participants {
                          gateNumber
                          earnings
                          stake
                          startingPoints
                          points
                          finishPosition
                          sectionalPositions
                          augments {
                              id
                              name
                            }
                          augmentsTriggered
                          horse {
                            id
                            name
                            bloodline
                            generation
                            gender
                            speedRating
                            sprintRating
                            enduranceRating
                            state
                            userId
                            user {
                              stableName
                            }
                          }
                        }
                      }
                    }
                  }
                }
                """,
                "variables": {"where": {"entityTypename": "Race"}}
            }
        }))
        print("📡 Subscribed to RaceEvents")

        while True:
            raw = await ws.recv()
            try:
                data = json.loads(raw)
                event = data.get("payload", {}).get("data", {}).get("raceEvent")
                if not event or event.get("entity") is None:
                    continue

                race = event["entity"]
                if race.get("status") != "FINISHED":
                    continue

                participants_data = race.get("participants", [])
                if not participants_data:
                    continue

                race_id = race["id"]
                participants = []

                for p in participants_data:
                    horse = p["horse"]
                    user_id = horse.get("userId", "00000000-0000-0000-0000-000000000000")

                    await upsert_horse({
                        "id": horse["id"],
                        "name": horse["name"],
                        "bloodline": horse["bloodline"],
                        "generation": horse["generation"],
                        "gender": horse.get("gender", "UNKNOWN"),
                        "rating": 0,
                        "speed_rating": horse.get("speedRating", 0),
                        "sprint_rating": horse.get("sprintRating", 0),
                        "endurance_rating": horse.get("enduranceRating", 0),
                        "state": horse.get("state", "UNKNOWN")
                    })

                    await upsert_stable({
                        "user_id": user_id,
                        "stable_name": horse.get("user", {}).get("stableName", "")
                    })

                    augments = p.get("augments", [])
                    augments += [None] * (3 - len(augments))
                    cpu_augment, ram_augment, hydraulic_augment = augments[:3]

                    triggers = p.get("augmentsTriggered", [])
                    triggers += [False] * (3 - len(triggers))
                    cpu_triggered, ram_triggered, hydraulic_triggered = triggers[:3]

                    participants.append({
                        "id": str(uuid.uuid4()),
                        "race_id": race_id,
                        "horse_id": horse["id"],
                        "user_id": user_id,
                        "gate_number": p.get("gateNumber"),
                        "finish_position": p.get("finishPosition"),
                        "finish_time": race["finishTime"],
                        "earnings": p.get("earnings", 0),
                        "stake": p.get("stake", 0),
                        "odds": 0,
                        "starting_points": p.get("startingPoints", 0),
                        "ending_points": p.get("points", 0),
                        "points_change": p.get("points", 0) - p.get("startingPoints", 0),
                        "cpu_augment": cpu_augment,
                        "ram_augment": ram_augment,
                        "hydraulic_augment": hydraulic_augment,
                        "cpu_triggered": cpu_triggered,
                        "ram_triggered": ram_triggered,
                        "hydraulic_triggered": hydraulic_triggered,
                        "sectional_positions": p.get("sectionalPositions", [])
                    })

                await insert_race_and_participants(race, participants)
                print(f"✅ Logged race {race['name']} ({race_id})")

            except Exception as e:
                print("❌ Error:", e)
                print("🔴 Raw:", raw)

# === RUN ===
asyncio.run(main())
