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
# from vicon_core_api import *
# from shogun_live_api import *
import src.utils.utils as utils
import sys
import os
import time
# get the path to the Shogun SDK
sys.path.append(r"C:\Program Files\Vicon\ShogunLive1.13\SDK\Python\shogun_live_api")
sys.path.append(r"C:\Program Files\Vicon\ShogunLive1.13\SDK\Python\vicon_core_api")

# Import the shogun_live_api package
import shogun_live_api
import vicon_core_api

# get the cur path to current folder for importing shogunPostFuncs
cur_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_path)

try:
    import shogunPostFuncs as spf
    from shogun_live_api.interfaces.capture_services import CaptureServices
    from vicon_core_api.client import Client, RPCError
except ImportError as e:
    print(f"ImportError: {str(e)}")
    sys.exit(1)

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
        self.vicon_client = Client(self.SHOGUN_IP, args.shogun_port)
        utils.check_connected(self.vicon_client)
        # Create required Shogun Live API services.
        self.vicon_capture_services = CaptureServices(self.vicon_client)

        self.SHOGUN_POST = spf.ViconShogunPost()
        self.last_path = self.get_capture_folder_shogun()

        print("Control API for Vicon Shogun Live initialized.")

    def start_record_osc_shogun(self):
        """
        Start recording via OSC and Shogun.
        """
        self.OSC_client.send_message("/RecordStart", [])
        self.vicon_capture_services.start_capture()

    async def stop_record_osc_shogun(self):
        """
        Stop recording via OSC and Shogun.
        """
        print("[OSC] Stopping the recording...")
        print("[Shogun] Stopping the recording...")

        folder = self.get_capture_folder_shogun()[1]
        name = self.vicon_capture_services.capture_name()[1]
        self.last_path = folder + "\\" + name + ".mcp"

        # Check if last path already exists and rename it to _old_{1} if it does
        if os.path.exists(self.last_path):
            print(f"File already exists: {self.last_path}")
            i = 1
            old_path = folder + "\\" + name + f"_old_{i}.mcp"
            while os.path.exists(old_path):
                i += 1
                old_path = folder + "\\" + name + f"_old_{i}.mcp"
            print(f"Renaming to: {old_path}")
            os.rename(self.last_path, old_path)

        self.OSC_client.send_message("/RecordStop", [])
        result = self.vicon_capture_services.stop_capture(0)
        print(f"Recording stopped. Result: {result}")
        self.open_last_file_shogun()

    def open_last_file_shogun(self):
        """
        Open the last recorded file in Shogun Live.
        """
        if self.SHOGUN_POST.shogun_post_connection_status == None:
            self.SHOGUN_POST = spf.ViconShogunPost()
            if self.SHOGUN_POST.shogun_post_connection_status == None:
                print("Failed to create Shogun POST connection.")
                return

        self.SHOGUN_POST.CloseFile()
        result = self.SHOGUN_POST.OpenFile(self.last_path)

        # Handle Error attribute correctly
        if hasattr(result, 'Error'):
            # Call the Error method to get the actual error message
            error_code = result.Error()  # Call it as a function

        # If error_code is True, then wait for 1 second and try again
        if error_code:
            print("Error occurred. Waiting for 1 second and trying again.")
            time.sleep(1)
            result = self.SHOGUN_POST.OpenFile(self.last_path)

    def set_file_name_osc_shogun(self, file_name):
        """
        Set file name for recording via OSC and Shogun.

        Args:
        - file_name (str): Name of the file.
        """
        if (file_name == ""):
            print("No file name provided.")
            return

        self.OSC_client.send_message("/SendFileNameToTCP", [file_name])
        self.OSC_client.send_message("/SetFileName", [file_name])
        print(f"Setting the file name to: '{file_name}'")
        self.vicon_capture_services.set_capture_name(file_name)

    def get_capture_folder_shogun(self):
        """
        Get the capture folder from Shogun Live API.
        """
        return self.vicon_capture_services.capture_folder()

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
