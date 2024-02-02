from pythonosc.udp_client import SimpleUDPClient

from vicon_core_api import *
from shogun_live_api import *
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
import asyncio

async def slaap():
    await asyncio.sleep(2)

ip = "192.168.0.180"
port = 8005
client = SimpleUDPClient(ip, port) 
# client.send_message("/RecordStart", [])
# asyncio.run(slaap())
# client.send_message("/RecordStop", [])


# client.send_message("/CloseTCPListener", [])
# client.send_message("/QuitServer", [])
# client.send_message("/SendFileNameToTCP", ["testFile"])