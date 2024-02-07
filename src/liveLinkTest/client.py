from pythonosc.dispatcher import Dispatcher
from typing import List, Any
from pythonosc.udp_client import SimpleUDPClient
import time

client = SimpleUDPClient("192.168.0.153", 8006)

# Send message and receive exactly one message (blocking)
client.send_message("/RecordStart", ["00:00:00.000", 12131])

time.sleep(1)


# client.send_message("/RecordStop", [])
# time.sleep(1)
# client.send_message("/Transport", ["192.168.0.226:9000", "blendshapeCSV"])
