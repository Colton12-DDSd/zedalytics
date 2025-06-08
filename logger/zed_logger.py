import asyncio
import websockets
import json
import uuid
from config import WS_URL, BEARER_TOKEN

async def main():
    async with websockets.connect(WS_URL, subprotocols=["graphql-transport-ws"]) as ws:
        # Init connection
        await ws.send(json.dumps({
            "type": "connection_init",
            "payload": {"authorization": BEARER_TOKEN}
        }))
        ack = await ws.recv()
        print(f"🟢 Connected: {ack}")

        # Subscribe to RaceEventSub
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
                            status
                          }
                        }
                      }
                    }
                """,
                "variables": {
                    "where": {"entityTypename": "Race"}
                }
            }
        }))
        print("📡 Subscribed to RaceEventSub (FINISHED only)")

        seen_finished = set()

        while True:
            raw = await ws.recv()
            try:
                data = json.loads(raw)
                race = data.get("payload", {}).get("data", {}).get("raceEvent", {}).get("entity")
                if not race:
                    continue

                race_id = race["id"]
                status = race["status"]
                name = race["name"]

                if status == "FINISHED" and race_id not in seen_finished:
                    seen_finished.add(race_id)
                    print(f"🏁 Race Finished: {name} (ID: {race_id})")

            except Exception as e:
                print("❌ Error:", e)
                print("🔴 Raw:", raw)

asyncio.run(main())
