# from pythonosc.udp_client import SimpleUDPClient

# from vicon_core_api import *
# from shogun_live_api import *
# from pythonosc import osc_server
# from pythonosc.dispatcher import Dispatcher
# import asyncio

# async def slaap():
#     await asyncio.sleep(2)

# ip = "192.168.0.180"
# port = 8005
# client = SimpleUDPClient(ip, port) 
# # client.send_message("/RecordStart", [])
# # asyncio.run(slaap())
# # client.send_message("/RecordStop", [])


# client.send_message("/CloseTCPListener", [])
# client.send_message("/QuitServer", [])
# # client.send_message("/SendFileNameToTCP", ["testFile"])
# client.send_message("/Alive", [])


# import asyncio
# import websockets

# async def send_messages():
#     uri = "ws://192.168.0.180:8009"
#     async with websockets.connect(uri) as websocket:
#         # Send "greet" message
#         # await websocket.send("greet:Hello, Server!")

#         await websocket.send("ping:a")
#         await websocket.send("fileName:test0204")
#         await asyncio.sleep(5)

#         await websocket.send("recordStart:starting the recording")
#         await asyncio.sleep(10)
#         await websocket.send("recordStop:stopping the recording")
#         await asyncio.sleep(2)


#         # Send "close" message
#         await websocket.send("close:a")

# asyncio.run(send_messages())

from pythonosc.udp_client import SimpleUDPClient

def set_filename(ip, port, filename):
    """
    Send the file name to the specified address via OSC.

    Args:
    - ip (str): The IP address of the OSC server.
    - port (int): The port of the OSC server.
    - filename (str): The filename to be set.
    """
    # Create the UDP client for sending messages
    client = SimpleUDPClient(ip, port)
    
    # Send the filename using the "/Slate" OSC address
    client.send_message("/Slate", [filename])
    print(f"Filename '{filename}' sent to {ip}:{port}")

def set_take_number(ip, port, take_number):
    """
    Send the take number to the specified address via OSC.

    Args:
    - ip (str): The IP address of the OSC server.
    - port (int): The port of the OSC server.
    - take_number (int): The take number to be set.
    """
    # Create the UDP client for sending messages
    client = SimpleUDPClient(ip, port)
    
    # Send the take number using the "/Take" OSC address
    client.send_message("/Take", [take_number])
    print(f"Take number '{take_number}' sent to {ip}:{port}")

if __name__ == "__main__":
    # Configuration
    llf_udp_ip = "192.168.0.246"  # IP of vislabApple
    llf_udp_port = 8006           # Port of vislabApple
    filename = "IAmAHuman"  # Replace with the desired filename
    take_number = 666  # Replace with the desired filename

    # Call the function to send the filename
    set_filename(llf_udp_ip, llf_udp_port, filename)
    set_take_number(llf_udp_ip, llf_udp_port, take_number)