import asyncio
import websockets
import time

# this is the time between "ticks"
# we can update it from a websocket message to be some other value 
timer_interval = 1

# this is a coroutine which runs continuously, printint out a message after 
# `timer_interval` number of seconds. It could call a function, advance the simulation etc. 
async def each_interval():
    while True:
        await asyncio.sleep(timer_interval)
        print(f"at time: ${time.time()}, on interval: {timer_interval}")

# handle the websocket connection and process incoming messages
async def handleMessage(message):
        parts = message.split(":")
        command_name = parts[0]
        print(f"Handling websocket request, message: {message}")
        if parts[0] == "settime":
            global timer_interval
            timer_interval = float(parts[1])
            print(f"Updating timer_interval: {timer_interval}")
            
# this starts the websocket server and keeps it running
async def start_ws():
    # Start the websocket server and run forever waiting for requests
    async with websockets.connect('ws://localhost:8765') as websocket:
        print(f"opened websocket")
        async for message in websocket:
            print(f"got message: {message}")
            await handleMessage(message)
        #await asyncio.Future()  # run forever

async def main():
    # we create asyncio tasks for each of the operations we want to run
    websocket_task = asyncio.create_task(start_ws())
    timer_task = asyncio.create_task(each_interval())
    # this starts each task. As they never complete, it runs continuously
    await asyncio.gather(websocket_task, timer_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        print("Closing loop")

