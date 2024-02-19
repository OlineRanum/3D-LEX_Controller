'''
File: controlAPI.py

Description:
This script defines the Control class, which serves as an intermediary for communication
between various components including OSC (Open Sound Control), Vicon Core API, Shogun Live API,
and other utilities. The class provides methods for controlling recording operations,
setting file names, closing connections and servers, and checking the status of servers.

Functions:
start_record_osc_shogun(): Initiates the recording process using OSC and Shogun.
stop_record_osc_shogun(): Stops the recording process using OSC and Shogun.
set_file_name_osc_shogun(file_name): Sets the file name for recording using OSC and Shogun.
close_osc_iphone(): Closes connections and servers related to OSC and iPhone.
servers_alive(): Checks if all servers are still operational and responsive.

Usage:
Instantiate the Control class with appropriate arguments, then utilize its methods to manage
recording operations, handle file naming, and monitor server status within the system.

Note:
Ensure correct configuration of IP addresses, ports, and other settings in the arguments
provided to the Control class during instantiation.
'''
from pythonosc.udp_client import SimpleUDPClient
from vicon_core_api import *
from shogun_live_api import *
from shogun_live_api import CaptureServices
from vicon_core_api import Client
import src.utils.utils as utils

class Control:
    def __init__(self, args):
        """
        Control class for managing recording and server connections.

        Args:
        - args: arguments containing target IP addresses, ports, and other parameters.

        Attributes:
        - PC_IP (str): Target IP address for the PC.
        - PORT_TCP_IPHONE (int): TCP port for iPhone communication.
        - SHOGUN_IP (str): Hostname/IP of the Shogun server.
        - OSC_client (SimpleUDPClient): UDP client for OSC communication.
        - PORT (int): Controller port.
        - vicon_client (Client): Vicon Core API client.
        - vicon_capture_services (CaptureServices): Shogun Live API services for Vicon capture.

        Methods:
        - start_record_osc_shogun: Start recording via OSC and Shogun.
        - stop_record_osc_shogun: Stop recording via OSC and Shogun.
        - set_file_name_osc_shogun: Set file name for recording via OSC and Shogun.
        - close_osc_iphone: Close connections and servers for OSC and iPhone.
        - servers_alive: Check if all servers are still alive.
        """
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

    def start_record_osc_shogun(self):
        """
        Start recording via OSC and Shogun.
        """
        self.OSC_client.send_message("/RecordStart", [])
        self.vicon_capture_services.start_capture()

    def stop_record_osc_shogun(self):
        """
        Stop recording via OSC and Shogun.
        """
        self.OSC_client.send_message("/RecordStop", [])
        self.vicon_capture_services.stop_capture(0)

    def set_file_name_osc_shogun(self, file_name):
        """
        Set file name for recording via OSC and Shogun.

        Args:
        - file_name (str): Name of the file.
        """
        self.OSC_client.send_message("/SendFileNameToTCP", [file_name])
        self.vicon_capture_services.set_capture_name(file_name)

    def close_osc_iphone(self):
        """
        Close connections and servers for OSC and iPhone.
        """
        self.OSC_client.send_message("/CloseTCPListener", [])
        self.OSC_client.send_message("/QuitServer", [])

    def servers_alive(self):
        """
        Check if all servers are still alive.
        """
        self.OSC_client.send_message("/Alive", [])
        utils.check_connected(self.vicon_client)
