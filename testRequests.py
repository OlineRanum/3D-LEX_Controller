from pythonosc.udp_client import SimpleUDPClient

from vicon_core_api import *
from shogun_live_api import *
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher

ip = "192.168.0.180"
port = 8005
client = SimpleUDPClient(ip, port) 
# client.send_message("/RecordStop", [])
client.send_message("/QuitServer", [])
