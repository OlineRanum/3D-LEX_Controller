import asyncio
import websockets
import ssl
import json
import asyncio

from src.config.setup import SetUp
args = SetUp("config.yaml")

async def send_message(msg):
    uri = f"ws://{args.websock_ip}:{args.websock_port}"
    async with websockets.connect(uri) as websocket:
        await websocket.send(msg)

async def handle_message(set_value, handler_value):
    """
    Handle the incoming message.

    Description:
    This function handles the incoming message from the WebSocket server.
    It prints the message to the console.

    Args:
    - set_value: The value to set.
    - handler_value: The handler value.

    Returns:
    None
    """
    print(f"Received message\tsetVal: {set_value}\thandleVal: {handler_value}")
    if (set_value == "startRecord"):
        print("Starting the recording")
        await send_message("recordStart:starting the recording")
    elif (set_value == "stopRecord"):
        print("Stopping the recording")
        await send_message("recordStop:stopping the recording")
    elif (handler_value == "broadcastGlos"):
        print(f"Setting the filename to: {set_value}")
        await send_message(f"fileName:{set_value}")
    elif (set_value == "broadcastGlos"):
        print("Sending a broadcast message")
        await send_message(f"fileName:{handler_value}")
    elif (handler_value == "glosName"):
        print(f"Setting the filename to: {set_value}")
        await send_message(f"fileName:{set_value}")
    else:
        print("Invalid message")

async def receive_messages():
    uri = args.leffe_con
    ssl_context = ssl.SSLContext()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with websockets.connect(uri, ssl=ssl_context) as websocket:
        print("Connected to server")
        while True:
            try:
                message = await websocket.recv()
                print("Received message:", message)
                
                # Parse the JSON message
                parsed_message = json.loads(message)

                # Extract values from the parsed message
                set_value = parsed_message.get('set', '')
                handler_value = parsed_message.get('handler', '')

                # Handle the message
                await handle_message(set_value, handler_value)

            except websockets.ConnectionClosed:
                print("Connection to server closed")
                break


loop = asyncio.get_event_loop()
try:
    # Start the server within the existing event loop
    loop.run_until_complete(receive_messages())
    loop.run_forever()
finally:
    # Clean up the event loop
    loop.close()
