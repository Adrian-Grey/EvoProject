import sys
import asyncio
import websockets

#reworked to use command line input instead of preset

async def sim_command(command):
    async with websockets.connect("ws://localhost:8765") as websocket:
        print("run_simulation got websocket connection")
        await websocket.send(f"{command}")
        print("sent query")
        print(f"{await websocket.recv()}")

async def main():
    print("Enter command:")
    command = input()
    await sim_command(command)

if __name__ == "__main__":
    asyncio.run(main())
