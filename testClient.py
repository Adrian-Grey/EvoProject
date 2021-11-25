import asyncio
import websockets

async def hello():
    async with websockets.connect("ws://localhost:8765") as websocket:
        await websocket.send("getPop")
        print(f"{await websocket.recv()}")

asyncio.run(hello())
