import asyncio
import websockets
import json
import uuid
from config import WS_URL, BEARER_TOKEN

logged_race_ids = set()

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
                          finishTime
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
                    continue

                race = race_event.get("entity")
                if not race or race.get("status") != "FINISHED":
                    continue

                race_id = race.get("id")
                if race_id in logged_race_ids:
                    continue
                logged_race_ids.add(race_id)

                print(f"\n🏁 Race Finished: {race['name']}")
                for p in race.get("participants", []):
                    horse = p.get("horse", {})
                    print(f" - 🐎 {horse.get('name')} (Bloodline: {horse.get('bloodline')}) | Gate {p.get('gateNumber')} → Finish {p.get('finishPosition')} in {p.get('finishTime')}s")

                await asyncio.sleep(10)  # prevent rapid re-processing

            except Exception as e:
                print("❌ Error:", e)
                print("🔴 Raw:", raw)

asyncio.run(main())
