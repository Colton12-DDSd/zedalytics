import asyncio
import websockets
import json
import uuid
from config import WS_URL, BEARER_TOKEN

async def main():
    async with websockets.connect(WS_URL, subprotocols=["graphql-transport-ws"]) as ws:
        await ws.send(json.dumps({
            "type": "connection_init",
            "payload": {"authorization": BEARER_TOKEN}
        }))
        ack = await ws.recv()
        print(f"🟢 Connected: {ack}")

        op_id = str(uuid.uuid4())
        await ws.send(json.dumps({
            "id": op_id,
            "type": "subscribe",
            "payload": {
                "operationName": "RaceEventSub",
                "query": """
                subscription RaceEventSub($where: SimpleEntityEventWhereInput) {
                  raceEvent(where: $where) {
                    entity {
                      ... on Race {
                        id
                        name
                        startTime
                        finishTime
                        racePotsTotal
                        participants {
                          gateNumber
                          finishPosition
                          finishTime
                          earnings
                          stake
                          startingPoints
                          sectionalPositions
                          augments {
                            __typename
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
                            user {
                              id
                              stable {
                                name
                              }
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
        print("📡 Subscribed to RaceEventSub (corrected)")

        seen_race_ids = set()

        while True:
            raw = await ws.recv()
            try:
                data = json.loads(raw)
                race = data.get("payload", {}).get("data", {}).get("raceEvent", {}).get("entity")
                if not race or race.get("id") in seen_race_ids or race.get("finishTime") is None:
                    continue

                seen_race_ids.add(race["id"])
                print(f"\n🏁 Race Finished: {race['name']} (ID: {race['id']})")

                for p in race.get("participants", []):
                    horse = p.get("horse", {})
                    user = horse.get("user", {})
                    stable = user.get("stable", {})

                    augments = [a.get("__typename", "None") for a in p.get("augments", [])]
                    triggers = p.get("augmentsTriggered", [])

                    while len(augments) < 3:
                        augments.append("None")
                    while len(triggers) < 3:
                        triggers.append(False)

                    print({
                        "race_id": race["id"],
                        "race_name": race["name"],
                        "race_date": race["startTime"],
                        "race_pots_total": race.get("racePotsTotal"),
                        "user_id": user.get("id"),
                        "stable_name": stable.get("name"),
                        "gate_number": p.get("gateNumber"),
                        "horse_id": horse.get("id"),
                        "horse_name": horse.get("name"),
                        "bloodline": horse.get("bloodline"),
                        "generation": horse.get("generation"),
                        "gender": horse.get("gender"),
                        "speed_rating": horse.get("speedRating"),
                        "sprint_rating": horse.get("sprintRating"),
                        "endurance_rating": horse.get("enduranceRating"),
                        "finish_position": p.get("finishPosition"),
                        "finish_time": p.get("finishTime"),
                        "earnings": p.get("earnings"),
                        "stake": p.get("stake"),
                        "starting_points": p.get("startingPoints"),
                        "sectional_positions": p.get("sectionalPositions"),
                        "cpu_augment": augments[0],
                        "ram_augment": augments[1],
                        "hydraulic_augment": augments[2],
                        "cpu_augment_triggered": int(triggers[0]),
                        "ram_augment_triggered": int(triggers[1]),
                        "hydraulic_augment_triggered": int(triggers[2]),
                    })

            except Exception as e:
                print("❌ Error:", e)
                print("🔴 Raw:", raw)

asyncio.run(main())
