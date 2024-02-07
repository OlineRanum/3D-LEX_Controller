import asyncio
import websockets
from src.config.setup import SetUp
from src.utils.controlAPI import Control
import functools

# Define a global event to signal when to stop the server
stop_server_event = asyncio.Event()

# Define functions to handle different types of messages
async def handle_close(websocket, control, message):
    print("Closing the server...")
    control.close_osc_iphone()
    await stop_server(control)
    await websocket.send("BYE")


async def handle_start(websocket, control, message):
    print("Asking OSC and Shogun to START record...")
    control.start_record_osc_shogun()
    await websocket.send("recording")


async def handle_stop(websocket, control, message):
    print("Asking OSC and Shogun to STOP record...")
    control.stop_record_osc_shogun()
    await websocket.send("stopping")


async def handle_ping(websocket, control, message):
    print("Asking OSC and Shogun to print...")
    control.servers_alive()
    await websocket.send("pong")


async def handle_filename(websocket, control, message):
    print("Asking OSC and Shogun to set the file name...")
    control.set_file_name_osc_shogun(message.split(':')[1].strip())
    await websocket.send("filename_set")


async def handle_greet(websocket, message):
    print(f"I have been greeted: {message}")
    await websocket.send("HELLO")


async def handle_default(websocket, message):
    print(f"Received message: {message}")
    await websocket.send("So What?")


# Define a function to handle incoming messages from clients
async def message_handler(control, websocket, path):
    message_handlers = {
        "close": functools.partial(handle_close, websocket, control),
        "recordStart": functools.partial(handle_start, websocket, control),
        "recordStop": functools.partial(handle_stop, websocket, control),
        "ping": functools.partial(handle_ping, websocket, control),
        "fileName": functools.partial(handle_filename, websocket, control),
        "greet": handle_greet,
    }

    async for message in websocket:
        print(f"Received message from client: {message}")
        message_type = message.split(':')[0].strip()
        handler = message_handlers.get(message_type, handle_default)
        await handler(message)

# Start the server
async def start_server(control, args):
    handler = functools.partial(message_handler, control)
    async with websockets.serve(handler, args.websock_ip, args.websock_port):
        print("Websocket Server started!")
        # Wait until the stop event is set
        await stop_server_event.wait()

# Function to stop the server
async def stop_server(control):
    control.close_osc_iphone()
    # Set the stop event to signal the server to stop
    stop_server_event.set()

if __name__ == "__main__":
    # Fetch args
    args = SetUp("config.yaml")

    # Create controller object
    control = Control(args)

    # Accept calls, and let the websockt control the controller
    asyncio.run(start_server(control, args))
