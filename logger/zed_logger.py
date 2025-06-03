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
                print("📦 Raw Event:")
                print(json.dumps(json.loads(raw), indent=2))
            except Exception as e:
                print(f"❌ Error decoding JSON: {e}")
                print("🔴 Raw:", raw)

# Reconnect loop
import time
async def run_forever():
    while True:
        try:
            await main()
        except Exception as e:
            print(f"❌ Disconnected with error: {e}")
            print("🔄 Reconnecting in 5 seconds...")
            time.sleep(5)

asyncio.run(run_forever())
