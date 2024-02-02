from pythonosc.udp_client import SimpleUDPClient
from vicon_core_api import *
from shogun_live_api import *
from shogun_live_api import CaptureServices
from vicon_core_api import Client
import utils

class Control:
    def __init__(self, args):
        self.PC_IP = args.target_ip
        self.PORT_TCP_IPHONE = args.TCP_Iphone_port
        self.SHOGUN_IP = args.shogun_hostname
        self.OSC_client = SimpleUDPClient(self.PC_IP, args.target_port) 
        self.PORT = args.controller_port

        # Connect Vicon Core API client to the application.
        with Client(self.PC_IP, args.shogun_port) as client:
            self.vicon_client = client
            utils.check_connected(client)
            # Create required Shogun Live API services.
            self.vicon_capture_services = CaptureServices(client)

    # Start record (OSC and shogun)
    def start_record_osc_shogun(self):
        self.OSC_client.send_message("/RecordStart", [])
        self.vicon_capture_services.start_capture()

    # Stop record (OSC and shogun)
    def stop_record_osc_shogun(self):
        self.OSC_client.send_message("/RecordStop", [])
        self.vicon_capture_services.stop_capture()

    # Send FileName (OSC and shogun)
    def set_file_name_osc_shogun(self, file_name):
        self.OSC_client.send_message("/SendFileNameToTCP", [file_name])
        self.vicon_capture_services.set_capture_name(file_name)

    # Close connections and servers (OSC, IPhone)
    def close_osc_iphone(self):
        self.OSC_client.send_message("/QuitServer", [])
        self.OSC_client.send_message("/CloseTCPListener", [])

    # Are all servers still alive? We expect prints from them
    def servers_alive(self, timeouttime):
        self.OSC_client.send_message("/Alive", [])
        utils.check_connected(self.vicon_client)
