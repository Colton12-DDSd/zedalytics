import asyncio
import websockets
import json
import uuid
from config import WS_URL, BEARER_TOKEN

async def main():
    async with websockets.connect(WS_URL, subprotocols=["graphql-transport-ws"]) as ws:
        # Initialize connection
        await ws.send(json.dumps({
            "type": "connection_init",
            "payload": {"authorization": BEARER_TOKEN}
        }))
        ack = await ws.recv()
        print(f"🟢 Connected: {ack}")

        # Subscribe to RaceEvent with a simple query
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
        print("📡 Subscribed to RaceEventSub (basic test)")

        # Event loop
        while True:
            raw = await ws.recv()
            try:
                data = json.loads(raw)
                race = data.get("payload", {}).get("data", {}).get("raceEvent", {}).get("entity")
                if race:
                    print(f"🔁 Race Update: {race['name']} | Status: {race['status']}")
            except Exception as e:
                print("❌ Error:", e)
                print("🔴 Raw:", raw)

asyncio.run(main())
