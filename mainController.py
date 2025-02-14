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
from src.utils.opticalCamera import FFmpegRecorder
import src.utils.OBSRecorder.src.obsRecording as obsRecording
from src.utils.popUp import PopUp
import functools
import os
import ssl

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
    print("[main] Closing the server...")
    control.close_osc_iphone()
    await stop_server(control)
    await websocket.send("BYE")


async def handle_start(websocket, control, optical_cameras, obs, message):
    """
    Handle the "recordStart" command.

    Description:
    This function handles the "recordStart" command received from the client.
    It instructs the OSC and Shogun servers to start recording and sends a
    "recording" message back to the client.

    Returns:
    None
    """
    print("[main] Asking OSC and Shogun to START record...")
    control.start_record_osc_shogun()

    print("[main] Asking optical camera to START record...")
    try:
        for optical_camera in optical_cameras:
            optical_camera.start_record()
    except Exception as e:
        print(f"[main] Error starting optical camera: {e}")

    try:
        obs.start_recording()
    except Exception as e:
        print(f"[main] Error starting OBS recording: {e}")

    await websocket.send("recording")


async def handle_stop(websocket, control, optical_cameras, obs, message):
    """
    Handle the "recordStop" command.

    Description:
    This function handles the "recordStop" command received from the client.
    It instructs the OSC, Shogun servers, and all optical cameras to stop recording,
    and sends a "stopping" message back to the client.

    Returns:
    None
    """
    print("[main] Asking OSC, Shogun, and cameras to STOP record...")

    try:
        # Create tasks for stopping all cameras and stopping OSC/Shogun
        tasks = [
            asyncio.to_thread(camera.stop_record) for camera in optical_cameras
        ] + [asyncio.to_thread(control.stop_record_osc_shogun)] + [asyncio.to_thread(obs.stop_recording)]

        # Run all tasks concurrently and wait for them to finish
        await asyncio.gather(*tasks)
    except Exception as e:
        print(f"[main ERROR] stopping recordings: {e}")

    # Send the "stopping" message to the client after all tasks are done
    try:
        await websocket.send("stopping")
    except websockets.exceptions.ConnectionClosedOK:
        print("[main] WebSocket connection already closed.")
    except Exception as e:
        print(f"[main ERROR] sending message: {e}")


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
    print("[main] Asking OSC and Shogun to print...")
    control.servers_alive()
    await websocket.send("pong")


async def handle_filename(websocket, control, optical_cameras, obs, message):
    """
    Handle the "fileName" command.

    Description:
    This function handles the "fileName" command received from the client.
    Sets the file name using the provided message and sends a "filename_set"
    message back to the client.

    Returns:
    None
    """
    file_name = message.split(':')[1].strip()
    print("[main] Asking OSC and Shogun to set the file name...")
    control.set_file_name_osc_shogun(file_name)

    print("[main] Asking optical camera to set the file name...")
    try:
        for optical_camera in optical_cameras:
            optical_camera.set_recording_name(file_name + "_" + optical_camera.video_device)
    except Exception as e:
        print(f"[main] Error setting optical camera file name: {e}")

    try:
        obs.set_save_location(None, vid_name=file_name)
    except Exception as e:
        print(f"[main] Error setting OBS file name: {e}")

    await websocket.send("filename_set")


async def handle_greet(message):
    print(f"[main] I have been greeted: {message}")


async def handle_default(message):
    print(f"[main] Received message: {message}")


# Define a function to handle incoming messages from clients
async def message_handler(control, optical_cameras, obs, websocket, path):
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
        "recordStart": functools.partial(handle_start, websocket, control, optical_cameras, obs),
        "recordStop": functools.partial(handle_stop, websocket, control, optical_cameras, obs),
        "ping": functools.partial(handle_ping, websocket, control),
        "fileName": functools.partial(handle_filename, websocket, control, optical_cameras, obs),
        "greet": handle_greet,
    }

    async for message in websocket:
        print(f"[main] Received message from client: {message}")
        message_type = message.split(':')[0].strip()
        handler = message_handlers.get(message_type, handle_default)
        await handler(message)

async def start_server(control, optical_cameras, obs=None, args=None):
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
    handler = functools.partial(message_handler, control, optical_cameras, obs)
    async with websockets.serve(handler, args.websock_ip, args.websock_port):
        print("[main] Websocket Server started!")
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

    popUp = PopUp()

    obs = obsRecording.OBSController(args.obs_host, args.obs_port, args.obs_password, popUp=PopUp())
    
    if obs.statusCode == obsRecording.OBSStatus.NOT_CONNECTED or obs.statusCode == obsRecording.OBSStatus.ERROR:
        print("OBS not connected or turned off. Please check the connection and try again if you want OBS recordings.")
    else:
        obs.set_save_location(args.obs_save_folder, vid_name="testb")
        obs.set_buffer_folder(args.obs_buffer_folder)

    optical_cameras = []
    for i in range(len(args.camera_names)):
        print(f"Camera {i + 1}: {args.camera_names[i]}, {args.camera_mic_names[i]}, {args.camera_save_paths[i]}")
        # Start the optical camera
        optical_camera = FFmpegRecorder(video_device=args.camera_names[i], audio_device=args.camera_mic_names[i], save_path=args.camera_save_paths[i], popUp=popUp)
        optical_camera.set_save_location(args.camera_save_paths[i])
        # optical_camera.set_save_location('D:\\VideoCapture')  # Set your desired save location
        if optical_camera.validate_devices() == (True, True) or optical_camera.validate_devices() == (True, False):
            optical_cameras.append(optical_camera)


    # Accept calls, and let the websockt control the controller
    # asyncio.run(start_server(control, args))


    # Create and run the event loop
    loop = asyncio.get_event_loop()
    try:
        # Start the server within the existing event loop
        loop.run_until_complete(start_server(control, optical_cameras, obs, args))
        loop.run_forever()
    finally:
        # Clean up the event loop
        loop.close()