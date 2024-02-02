from pythonosc.udp_client import SimpleUDPClient
from vicon_core_api import *
from shogun_live_api import *
from shogun_live_api import CaptureServices
from vicon_core_api import Client
import src.utils.utils as utils

class Control:
    def __init__(self, args):
        self.PC_IP = args.target_ip
        self.PORT_TCP_IPHONE = args.tcp_iphone_port
        self.SHOGUN_IP = args.shogun_hostname
        self.OSC_client = SimpleUDPClient(self.PC_IP, args.target_port) 
        self.PORT = args.controller_port

        # Connect Vicon Core API client to the application.
        self.vicon_client = Client(self.PC_IP, args.shogun_port)
        utils.check_connected(self.vicon_client)
        # Create required Shogun Live API services.
        self.vicon_capture_services = CaptureServices(self.vicon_client)

    # Start record (OSC and shogun)
    def start_record_osc_shogun(self):
        self.OSC_client.send_message("/RecordStart", [])
        self.vicon_capture_services.start_capture()

    # Stop record (OSC and shogun)
    def stop_record_osc_shogun(self):
        self.OSC_client.send_message("/RecordStop", [])
        self.vicon_capture_services.stop_capture(0)

    # Send FileName (OSC and shogun)
    def set_file_name_osc_shogun(self, file_name):
        self.OSC_client.send_message("/SendFileNameToTCP", [file_name])
        self.vicon_capture_services.set_capture_name(file_name)

    # Close connections and servers (OSC, IPhone)
    def close_osc_iphone(self):
        self.OSC_client.send_message("/CloseTCPListener", [])
        self.OSC_client.send_message("/QuitServer", [])

    # Are all servers still alive? We expect prints from them
    def servers_alive(self):
        self.OSC_client.send_message("/Alive", [])
        utils.check_connected(self.vicon_client)
