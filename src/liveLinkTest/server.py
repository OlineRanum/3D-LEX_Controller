from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio
from pythonosc.udp_client import SimpleUDPClient
client = SimpleUDPClient("192.168.0.247", 8000)


def RecordStartConfirm (timecode, iets):
    print(timecode, iets)

def RecordStopConfirm (timecode, blendshapeCSV, referenceMOV, *args):
    print(timecode, blendshapeCSV, referenceMOV, *args)
    client.send_message("/Transport", ["192.168.0.226:9000", referenceMOV])

def Transport(iets, iets2):
    print(iets,iets2)

dispatcher = Dispatcher()
dispatcher.map("/RecordStartConfirm", RecordStartConfirm)
dispatcher.map("/RecordStopConfirm", RecordStopConfirm)
dispatcher.map("/Transport", Transport)


ip = "192.168.0.226"
port = 6000


async def loop():
    """Example main loop that only runs for 10 iterations before finishing"""
    for i in range(10):
        print(f"Loop {i}")
        await asyncio.sleep(1)


async def init_main():
    server = AsyncIOOSCUDPServer((ip, port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving

    await loop()  # Enter main loop of program

    transport.close()  # Clean up serve endpoint


asyncio.run(init_main())