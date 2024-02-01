from pythonosc.udp_client import SimpleUDPClient
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
import asyncio
from asyncio import run 
import os 

# Class LiveLinkFaceClient sends messages to the live link server on the IPhone
# Sometimes it will be requested to save the file by the python server, and other times
# it will be requested to send messages by the IO
class LiveLinkFaceClient:
    # The init starts the client and sets the python server address on the IPhone
    def __init__(self, args, gloss):
        self.client = SimpleUDPClient(args.llf_udp_ip, args.llf_udp_port)
        self.client.send_message("/OSCSetSendTarget", [args.target_ip, args.target_port])
        self.client.send_message("/VideoDisplayOn", [])
        self.gloss = gloss
        self.args = args

        # Set gloss of first sign
        self.set_filename(self.gloss)
        self.takenumber = 0
    
    def start_capture(self):
        self.client.send_message("/RecordStart", [self.gloss, self.takenumber])
        return self.takenumber

    def stop_capture(self):
        self.client.send_message("/RecordStop", [])
        self.takenumber += 1
        # self.save_file()

    def set_filename(self, gloss):
        self.gloss = gloss
        self.client.send_message("/Slate", [self.gloss])
        self.takenumber = 0
    
    def request_battery(self):
        self.client.send_message("/BatteryQuery", [])

    def save_file(self, timecode, blendshapeCSV, referenceMOV, *args):
        # print(f"{args}")
        print("send the transport towards - " + self.args.target_ip + ':' + str(self.args.target_port))
        print(timecode, blendshapeCSV, referenceMOV, *args)
        # Ask our client to send a transport message to our server 
        self.client.send_message("/Transport", [self.args.target_ip + ':' + str(self.args.target_port), referenceMOV])

# Class LiveLinkFaceServer launches the live link server that communicates with the IPhone
# The IP used in this server should be the same as the listener in the IPhone
# The server is launched asynchronously and the main loop will continue afterwards
# Because the server also needs to confirm some messages of the IPhone, it uses some client functions from
# the LiveLinkFaceClient Class
class LiveLinkFaceServer:
    def __init__(self, controller):
        self.gloss = controller.gloss
        self.args = controller.args

        # Start server rules here, add a default rule for all other incoming messages
        self.dispatcher = Dispatcher()
        self.dispatcher.map("/OSCSetSendTargetConfirm", print)

        # When the recording is fully finished, instruct the client to save the file locally
        self.dispatcher.map("/RecordStopConfirm", controller.llfc.save_file)
        self.dispatcher.set_default_handler(self.default)

        # Launch Server
        run(self.init_server(controller))
        

    # Server async launch code and close code, serving on target ip and port
    async def init_server(self, controller):
        self.server = osc_server.AsyncIOOSCUDPServer(
            (self.args.target_ip, self.args.target_port), self.dispatcher, asyncio.get_event_loop())
        transport, protocol = await self.server.create_serve_endpoint()

        # Enter main program async
        await controller.start()
        print('we are here')

        # After we are done with the server, close it
        transport.close()

    # Print all messages by default
    def default(self, address, *args):
        print(f"{address}: {args}")