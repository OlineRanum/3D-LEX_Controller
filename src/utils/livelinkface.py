from pythonosc.udp_client import SimpleUDPClient
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
import asyncio
from asyncio import run 
import os 

class LiveLinkFaceClient:
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
        self.save_file()

    def set_filename(self, gloss):
        self.gloss = gloss
        self.client.send_message("/Slate", [self.gloss])
        self.takenumber = 0
    
    def request_battery(self):
        print('request battery')
        self.client.send_message("/BatteryQuery", [])


    def save_file(self, *args):
        print(f"{args}")
        self.client.send_message("/Transport", [self.args.target_ip + ':' + str(self.args.target_port), os.getcwd() + '\output'])
        print(os.getcwd() + '\output\\' + self.gloss)
        print(self.args.target_ip + ':' + str(self.args.target_port))
    
    def default(self, address, *args):
        print(f"{address}: {args}")

class LiveLinkFaceServer:
    def __init__(self, controller):
        self.gloss = controller.gloss
        self.args = controller.args
        self.dispatcher = Dispatcher()
        
        self.dispatcher.map("/RecordStop", controller.llfc.stop_capture)
        self.dispatcher.map("/OSCSetSendTargetConfirm", print)
        self.dispatcher.map("/volume", self.print_volume_handler, "Volume")
        #self.dispatcher.map("/RecordStopConfirm", controller.llfc.save_file, "fsaf")
        self.dispatcher.set_default_handler(controller.llfc.default)
        run(self.init_server(controller))
        

    async def init_server(self, controller):
        self.server = osc_server.AsyncIOOSCUDPServer(
            (self.args.target_ip, self.args.target_port), self.dispatcher, asyncio.get_event_loop())
        transport, protocol = await self.server.create_serve_endpoint()

        # enter main of program
        await controller.start()
        print('we are here')

        transport.close()
        

    def print_volume_handler(self, unused_addr, args, volume):
        print("[{0}] ~ {1}".format(args[0], volume))
    
    def print_compute_handler(self, unused_addr, args, volume):
        try:
            print("[{0}] ~ {1}".format(args[0], args[1](volume)))
        except ValueError:
            pass
    