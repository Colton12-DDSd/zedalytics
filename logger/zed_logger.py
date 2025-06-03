import asyncio
import websockets
import json
import uuid
from config import WS_URL, BEARER_TOKEN

seen_races = set()

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
                    entityTypename
                    entity {
                      ... on Race {
                        id
                        name
                        status
                        startTime
                        finishTime
                        participants {
                          gateNumber
                          finishPosition
                          horse {
                            id
                            name
                            bloodline
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
                race_event = data.get("payload", {}).get("data", {}).get("raceEvent", {})
                if not race_event:
                    print("⚠️ Skipping, missing raceEvent")
                    continue

                race = race_event.get("entity")
                if not race or race.get("status") != "FINISHED":
                    continue

                race_id = race.get("id")
                if race_id in seen_races:
                    continue  # Skip already-logged races
                seen_races.add(race_id)

                print(f"🏁 Race Finished: {race['name']}")
                for p in race.get("participants", []):
                    horse = p.get("horse", {})
                    print(f" - 🐎 {horse.get('name')} (Bloodline: {horse.get('bloodline')}) | Gate {p.get('gateNumber')} → Finish {p.get('finishPosition')}")

                await asyncio.sleep(10)  # Cooldown between races

            except Exception as e:
                print("❌ Error:", e)
                print("🔴 Raw:", raw)

asyncio.run(main())
