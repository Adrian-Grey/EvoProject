import sys
import asyncio
import websockets

async def get_population_count():
    print("get_population_count called")
    async with websockets.connect("ws://localhost:8765") as websocket:
        print("get_population_count got websocket connection")
        await websocket.send("getPop")
        print("sent getPop query")
        return(f"{await websocket.recv()}")

async def run_simulation():
    print("run_simulation called")
    async with websockets.connect("ws://localhost:8765") as websocket:
        print("run_simulation got websocket connection")
        await websocket.send("runSim,100")
        print("sent runSim query")
        await websocket.recv()

async def main():
    print(f"Initial population: {await get_population_count()}")
    print("Running sim...")
    await run_simulation()
    print(f"Final population: {await get_population_count()}")

if __name__ == "__main__":
    asyncio.run(main())
