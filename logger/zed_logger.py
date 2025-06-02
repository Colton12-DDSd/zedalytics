import asyncio
import websockets
import json
import uuid

# === CONFIG ===
BEARER_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImEwZTRjODg4LWYxYjktNGJhYS04NzkyLTQ5NDIxNTA2MjgzMyJ9.eyJraWQiOiJhMGU0Yzg4OC1mMWI5LTRiYWEtODc5Mi00OTQyMTUwNjI4MzMiLCJhdWQiOiJodHRwczovL2FwcC56ZWRjaGFtcGlvbnMuY29tIiwiaXNzIjoiYXBwLmR5bmFtaWNhdXRoLmNvbS9kZWRjYTIyNS1hNGUxLTQ0ZWMtYjk2NC01ZDE0ZmIyMjYwN2QiLCJzdWIiOiIxYmU5NDM3NS04NjA1LTQ4NWEtODQwYS01NzJhNmQ3MzNhMTAiLCJzaWQiOiIwNmNjYmMzOS05YzM5LTQ5YmQtYWZiYS0wNzNkMDliNmIyZjciLCJlbWFpbCI6ImNvbHRvbjEyLmNiQGdtYWlsLmNvbSIsImVudmlyb25tZW50X2lkIjoiZGVkY2EyMjUtYTRlMS00NGVjLWI5NjQtNWQxNGZiMjI2MDdkIiwibGlzdHMiOltdLCJtaXNzaW5nX2ZpZWxkcyI6W10sInZlcmlmaWVkX2NyZWRlbnRpYWxzIjpbeyJhZGRyZXNzIjoiMHg4OTBCMjNBRjkwNTc2Mzg0YUJkZDA4OTFFOGIwZDM0QzNlRkQxQTRDIiwiY2hhaW4iOiJlaXAxNTUiLCJpZCI6IjRjODgzMmNhLWM0MTMtNDE1Ny05YzkzLTAzZWM3ZmMzZjE0MiIsIm5hbWVfc2VydmljZSI6e30sInB1YmxpY19pZGVudGlmaWVyIjoiMHg4OTBCMjNBRjkwNTc2Mzg0YUJkZDA4OTFFOGIwZDM0QzNlRkQxQTRDIiwid2FsbGV0X25hbWUiOiJ0dXJua2V5aGQiLCJ3YWxsZXRfcHJvdmlkZXIiOiJlbWJlZGRlZFdhbGxldCIsIndhbGxldF9wcm9wZXJ0aWVzIjp7InR1cm5rZXlTdWJPcmdhbml6YXRpb25JZCI6IjcwMmIwOTVkLWNlMmEtNDdiZS05MmI4LTk5YzEwM2IyNzYwMyIsInR1cm5rZXlIRFdhbGxldElkIjoiMzNjNzY3OTgtOTMwZS01YzQ0LWExMDQtNGU0MTk0MGI5MmViIiwiaXNBdXRoZW50aWNhdG9yQXR0YWNoZWQiOmZhbHNlLCJ0dXJua2V5VXNlcklkIjoiYjdiZTRmODAtNDk5NS00OTEzLWFhMTEtYTgzNmVmMWM0YWFjIiwiaXNTZXNzaW9uS2V5Q29tcGF0aWJsZSI6dHJ1ZSwidmVyc2lvbiI6IlYyIn0sImZvcm1hdCI6ImJsb2NrY2hhaW4iLCJsYXN0U2VsZWN0ZWRBdCI6IjIwMjUtMDQtMThUMDM6MDM6NDIuMDE2WiIsInNpZ25JbkVuYWJsZWQiOmZhbHNlfSx7ImFkZHJlc3MiOiIweDk3YUU1NzIxM0JBMjY4NDIwMjIzZEI2NkY4ZDJGYjhDYzQyZkNmNDUiLCJjaGFpbiI6ImVpcDE1NSIsInNpZ25lclJlZklkIjoiNGM4ODMyY2EtYzQxMy00MTU3LTljOTMtMDNlYzdmYzNmMTQyIiwiaWQiOiJhNGVmNGViZC1iN2NjLTQ0ZmMtODk5NS1hNjUyOTY2NmI4NGQiLCJuYW1lX3NlcnZpY2UiOnt9LCJwdWJsaWNfaWRlbnRpZmllciI6IjB4OTdhRTU3MjEzQkEyNjg0MjAyMjNkQjY2RjhkMkZiOENjNDJmQ2Y0NSIsIndhbGxldF9uYW1lIjoiemVyb2RldiIsIndhbGxldF9wcm92aWRlciI6InNtYXJ0Q29udHJhY3RXYWxsZXQiLCJ3YWxsZXRfcHJvcGVydGllcyI6eyJlY2RzYVByb3ZpZGVyVHlwZSI6Inplcm9kZXZfc2lnbmVyX3RvX2VjZHNhIiwiZW50cnlQb2ludFZlcnNpb24iOiJ2NyIsImtlcm5lbFZlcnNpb24iOiJ2M18xIn0sImZvcm1hdCI6ImJsb2NrY2hhaW4iLCJsYXN0U2VsZWN0ZWRBdCI6IjIwMjUtMDYtMDFUMTc6NTY6MDguOTc5WiIsInNpZ25JbkVuYWJsZWQiOnRydWV9LHsiYWRkcmVzcyI6IjB4OUVGMjlkNzU0NDVCQUQ1OTVjMTJDOEM2OEEzMmRmRkI2NjBkRDQ3NiIsImNoYWluIjoiZWlwMTU1IiwiaWQiOiI1M2I4Yjc1Yy0zYjBhLTRhNjUtOTg2Ny00MzZkZDBiY2FkNTUiLCJuYW1lX3NlcnZpY2UiOnt9LCJwdWJsaWNfaWRlbnRpZmllciI6IjB4OUVGMjlkNzU0NDVCQUQ1OTVjMTJDOEM2OEEzMmRmRkI2NjBkRDQ3NiIsIndhbGxldF9uYW1lIjoibWV0YW1hc2siLCJ3YWxsZXRfcHJvdmlkZXIiOiJicm93c2VyRXh0ZW5zaW9uIiwiZm9ybWF0IjoiYmxvY2tjaGFpbiIsImxhc3RTZWxlY3RlZEF0IjoiMjAyNS0wNC0xN1QyMToyNzo1Ny4xNTFaIiwic2lnbkluRW5hYmxlZCI6dHJ1ZX0seyJlbWFpbCI6ImNvbHRvbjEyLmNiQGdtYWlsLmNvbSIsImlkIjoiNWUzMmEzNzQtMDQ5MS00NzYwLTlmYmEtNzEzYmRmNDI0OWEwIiwicHVibGljX2lkZW50aWZpZXIiOiJjb2x0b24xMi5jYkBnbWFpbC5jb20iLCJmb3JtYXQiOiJlbWFpbCIsInNpZ25JbkVuYWJsZWQiOnRydWV9LHsiaWQiOiJhZTQyNWY1ZC01NTY1LTRmN2QtODVkYi1hYjk1NTJiMGUwYmUiLCJwdWJsaWNfaWRlbnRpZmllciI6IkNvbHRvbiBCYXVzZXJtYW4iLCJmb3JtYXQiOiJvYXV0aCIsIm9hdXRoX3Byb3ZpZGVyIjoiZ29vZ2xlIiwib2F1dGhfdXNlcm5hbWUiOiJjb2x0b24xMi5jYkBnbWFpbC5jb20iLCJvYXV0aF9kaXNwbGF5X25hbWUiOiJDb2x0b24gQmF1c2VybWFuIiwib2F1dGhfYWNjb3VudF9pZCI6IjEwMTQzOTU0MTQyMzI2MTEyNDk3NCIsIm9hdXRoX2FjY291bnRfcGhvdG9zIjpbImh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0k0cElXbE13cVFHNnctM1AyX245aWV4bnNRcTNhNnpqaUxSelkzN0Z0VWxCLVRHUT1zOTYtYyJdLCJvYXV0aF9lbWFpbHMiOlsiY29sdG9uMTIuY2JAZ21haWwuY29tIl0sIm9hdXRoX21ldGFkYXRhIjp7fSwic2lnbkluRW5hYmxlZCI6ZmFsc2V9XSwibGFzdF92ZXJpZmllZF9jcmVkZW50aWFsX2lkIjoiYTRlZjRlYmQtYjdjYy00NGZjLTg5OTUtYTY1Mjk2NjZiODRkIiwiZmlyc3RfdmlzaXQiOiIyMDI1LTAzLTAzVDIyOjIxOjQxLjQ4NloiLCJsYXN0X3Zpc2l0IjoiMjAyNS0wNi0wMVQxNzo1NjowNy43MDRaIiwibmV3X3VzZXIiOmZhbHNlLCJtZXRhZGF0YSI6e30sInZlcmlmaWVkQ3JlZGVudGlhbHNIYXNoZXMiOnsiYmxvY2tjaGFpbiI6IjA3M2YzMmUwYTVmYzJkNjRhZTcyMGVmNjNlODA4NjI4IiwiZW1haWwiOiIyNjQ1NjEwNjNkZjg3M2M1MmRlZjE3NDU2NTkwOTU1NyIsIm9hdXRoIjoiNWM0ODhmMTFmMmMzODYwZDIyYTUzMmQ5YWFmYjUxNGIifSwiaWF0IjoxNzQ4ODAwNTY5LCJleHAiOjE3NDg4ODY5Njl9.RpZfKXiwChQ-OrAaBIeNopwC6tquRcKQknyplvjyuzNpHmbjiz-OD_OXpPNxem0dap6iEGWxV3d8BP26ZKw5fApRfKN3ycYX4O7ZSwXugqVybHNLVgqWowlBZnxAO5qtAMoAMkumngpBHCHsuyQebZRBp-EO4VTZJ7ul_VziIdx6sa_JtZlJ_AskW_jIxz6lz0FmUZyAy6-MLJn0M7KNrYZMy8RBoCilvAi2JA1LfsOX7nKM4G4crRhXy8P7W98CDncuH1HYuGLdlZvC4WgcfNWtOFOccIz2OUvZK3APMCHTh2BDl8LJ5JRlexgTqmDYjADV6qVk7ThLcD5KCIzGDMlvG_W_N7UvRDSTp29XiEhciB1-2dkKQRn7Gu6gwvkcRCeBEjJ2_Y9gCdCPD9v_dvODJoY-Aa1LSDx5pVbUSYrOL5uLOfLPKWoXnaRjxIANbs1o0W--D1iIP-4pZ9ZxLRlRbaJx0ytT-QwRvnsFjMduEjgAWQVx1ycBO-zPcJr-nTVTCPa7s_xm9aMUfrlWzdCq9Yx41NrgKgiZifnUJsOlNhwP2n0Q08GQ6t7h8zzGDS1z8h6_UintYH1Cx8zFjKkZcw0AGNrs9CsRPGdkzaEaROie2DVFqUkYxXaY5CAthgutkPGArKEjsxYkZmpisp8b3y3EBOzLSPm0LHMsPq0"
WS_URL = "wss://zedx-subscriptions.zedchampions.com/"

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
            print("\n🔴 Full Raw Dump:")
            print(json.dumps(json.loads(raw), indent=2))

# Run it
asyncio.run(main())
