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
                        participants {
                          gateNumber
                          finishPosition
                          sectionalPositions
                          augments
                          augmentsTriggered
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

        seen_race_ids = set()

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

                race_id = race["id"]
                if race_id in seen_race_ids:
                    continue
                seen_race_ids.add(race_id)

                print(f"\n🏁 Race Finished: {race['name']}")
                for p in race.get("participants", []):
                    horse = p.get("horse", {})
                    name = horse.get("name")
                    bloodline = horse.get("bloodline")
                    gate = p.get("gateNumber")
                    pos = p.get("finishPosition")
                    time = p.get("sectionalPositions", [None])[-1] or "??"

                    augments = [a.get("__typename", "None") for a in p.get("augments", [])]
                    triggers = p.get("augmentsTriggered", [])

                    # Pad to 3 augments
                    while len(augments) < 3:
                        augments.append("None")
                    while len(triggers) < 3:
                        triggers.append(False)

                    aug_display = ", ".join([
                        f"{a}{'✓' if t else '✗'}"
                        for a, t in zip(augments, triggers)
                    ])

                    print(f" - 🐎 {name} (Bloodline: {bloodline}) | Gate {gate} → Finish {pos} in {time}s | Augs: {aug_display}")

            except Exception as e:
                print("❌ Error:", e)
                print("🔴 Raw:", raw)

asyncio.run(main())
