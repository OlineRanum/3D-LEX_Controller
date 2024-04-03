"""
File: websocket_server.py

Description:
This script defines a WebSocket server that communicates with an OSC server and Shogun
to control recording operations. It listens for incoming messages from clients,
such as commands to start or stop recording, set filenames, and handle pings.

Functions:
- handle_close(websocket, control, message): Handle the "close" command.
- handle_start(websocket, control, message): Handle the "recordStart" command.
- handle_stop(websocket, control, message): Handle the "recordStop" command.
- handle_ping(websocket, control, message): Handle the "ping" command.
- handle_filename(websocket, control, message): Handle the "fileName" command.
- handle_greet(message): Handle the "greet" command.
- handle_default(message): Handle default messages.
- message_handler(control, websocket, path): Handle incoming messages from clients.
- start_server(control, args): Start the WebSocket server.
- stop_server(control): Stop the WebSocket server.

Usage:
Run the script to start the WebSocket server. The server listens for incoming messages
and communicates with an OSC server and Shogun to control recording operations based
on the received commands.

Note:
Ensure the configuration file (config.yaml) is properly configured with required settings.
"""
import asyncio
import websockets
from src.config.setup import SetUp
from src.utils.controlAPI import Control
import functools
import os

# Define a global event to signal when to stop the server
stop_server_event = asyncio.Event()

async def handle_close(websocket, control, message):
    """
    Handle the "close" command.

    Args:
    - websocket: The WebSocket connection.
    - control: An instance of the Control class for controlling OSC and Shogun.
    - message (str): The message received from the client.

    Description:
    This function handles the "close" command received from the client. It closes
    the OSC server connection, stops the server, and sends a "BYE" message back
    to the client.

    Returns:
    None
    """
    print("Closing the server...")
    control.close_osc_iphone()
    await stop_server(control)
    await websocket.send("BYE")


async def handle_start(websocket, control, message):
    """
    Handle the "recordStart" command.

    Description:
    This function handles the "recordStart" command received from the client.
    It instructs the OSC and Shogun servers to start recording and sends a
    "recording" message back to the client.

    Returns:
    None
    """
    print("Asking OSC and Shogun to START record...")
    control.start_record_osc_shogun()
    await websocket.send("recording")


async def handle_stop(websocket, control, message):
    """
    Handle the "recordStop" command.

    Description:
    This function handles the "recordStop" command received from the client.
    It instructs the OSC and Shogun servers to stop recording and sends a
    "stopping" message back to the client.

    Returns:
    None
    """
    print("Asking OSC and Shogun to STOP record...")
    control.stop_record_osc_shogun()
    await websocket.send("stopping")


async def handle_ping(websocket, control, message):
    """
    Handle the "ping" command.

    Description:
    This function handles the "ping" command received from the client.
    It instructs the OSC and Shogun servers to print their status and
    sends a "pong" message back to the client.

    Returns:
    None
    """
    print("Asking OSC and Shogun to print...")
    control.servers_alive()
    await websocket.send("pong")


async def handle_filename(websocket, control, message):
    """
    Handle the "fileName" command.

    Description:
    This function handles the "fileName" command received from the client.
    Sets the file name using the provided message and sends a "filename_set"
    message back to the client.

    Returns:
    None
    """
    print("Asking OSC and Shogun to set the file name...")
    control.set_file_name_osc_shogun(message.split(':')[1].strip())
    await websocket.send("filename_set")


async def handle_greet(message):
    print(f"I have been greeted: {message}")


async def handle_default(message):
    print(f"Received message: {message}")


# Define a function to handle incoming messages from clients
async def message_handler(control, websocket, path):
    """
    Handle incoming messages from clients.

    Description:
    This function handles incoming messages from clients and routes them
    to the appropriate message handlers based on the message type.

    Args:
    - control: An instance of the Control class for controlling OSC and Shogun.
    - websocket: The WebSocket connection.
    - path: The requested URI path sent by the client.

    Returns:
    None
    """
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

async def start_server(control, args):
    """
    Start the WebSocket server.

    Description:
    This function starts the WebSocket server and listens for incoming connections.
    It uses the message_handler function to handle incoming messages from clients.
    The server continues running until the stop_server_event is set.

    Args:
    - control: An instance of the Control class for controlling OSC and Shogun.
    - args: Command-line arguments.

    Returns:
    None
    """
    async with websockets.listen((args.websock_ip, args.websock_port)):
        print("Websocket Server started!")
        # Wait until the stop event is set
        await stop_server_event.wait()

async def stop_server(control):
    """
    Stop the WebSocket server.

    Description:
    This function stops the WebSocket server. It closes the OSC server connection
    and sets the stop_server_event to signal the server to stop.

    Args:
    - control: An instance of the Control class for controlling OSC and Shogun.

    Returns:
    None
    """
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
