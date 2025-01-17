"""
File: LiveLinkFace.py

Description:
This file defines the LiveLinkFaceClient and LiveLinkFaceServer classes for
communicating with an iPhone server via OSC (Open Sound Control) protocol.

Classes:
- LiveLinkFaceClient: Sends messages to the iPhone Live Link server.
- LiveLinkFaceServer: Launches the Live Link server and communicates with the iPhone.

LiveLinkFaceClient:
- The __init__ method initializes the client and sets the Python server address on the iPhone.
- The start_capture method instructs the iPhone to start capturing.
- The stop_capture method instructs the iPhone to stop capturing.
- The set_filename method sets the file name for capturing.
- The request_battery method requests the battery status from the iPhone.
- The save_file method sends a transport message to the iPhone to save a file.

LiveLinkFaceServer:
- The __init__ method initializes the server and client objects for communication with the iPhone.
- The init_server method starts the server to receive messages from the iPhone.
- The quit_server method exits the server and client.
- The start_recording method starts recording with the iPhone and TCP socket.
- The send_close_tcp method sends a close command to the TCP socket.
- The send_file_name_tcp method sends a file name to the TCP socket.
- The send_are_you_okay_tcp method checks if the TCP socket is okay.
- The send_signal_recording_tcp method sets the TCP socket to file receiving mode.
- The ping_back method responds to requests, indicating that the OSC server is alive.
- The default method prints all received messages by default.
"""
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import sys
import socket
import struct

class LiveLinkFaceClient:
    """
    Class LiveLinkFaceClient sends messages to the live link server on the iPhone.

    Methods:
    - __init__: Initializes the client and sets the Python server address on the iPhone.
    - start_capture: Sends a message to start capturing to the iPhone server.
    - stop_capture: Sends a message to stop capturing to the iPhone server.
    - set_filename: Sets the file name for capturing on the iPhone server.
    - request_battery: Requests battery information from the iPhone server.
    - save_file: Sends a transport message to the iPhone for saving a file.

    Attributes:
    - toIphone: SimpleUDPClient instance for communication with the iPhone server.
    - gloss: Current gloss set for capturing.
    - args: Arguments for configuring the client.
    """

    def __init__(self, args, gloss):
        """
        Initialize the LiveLinkFaceClient.

        Args:
        - args: The arguments containing necessary configurations.
        - gloss: The initial gloss for capturing.

        Description:
        This method initializes the LiveLinkFaceClient instance. It sets up the UDP client
        for communication with the iPhone server, sets the Python server address on the iPhone,
        and initializes other necessary attributes.
        """
        print("Sending to: ", args.llf_udp_ip, args.llf_udp_port)
        self.toIphone = SimpleUDPClient(args.llf_udp_ip, args.llf_udp_port)
        self.toIphone.send_message("/OSCSetSendTarget", [args.target_ip, args.target_port])
        self.toIphone.send_message("/VideoDisplayOn", [])
        self.gloss = gloss
        self.args = args

        # Set gloss of first sign
        self.set_filename(self.gloss)
        self.takenumber = 0

    def start_capture(self, *args):
        """
        Start capturing on the iPhone server.

        Returns:
        The current capture number.

        Description:
        This method sends a message to the iPhone server to start capturing.
        It increments the capture number and returns it.
        """
        self.toIphone.send_message("/RecordStart", [self.gloss, self.takenumber])
        return self.takenumber

    def stop_capture(self, *args):
        """
        Stop capturing on the iPhone server.

        Description:
        This method sends a message to the iPhone server to stop capturing.
        It also increments the capture number.
        """
        self.toIphone.send_message("/RecordStop", [])
        self.takenumber += 1

    def set_filename(self, gloss, *args):
        """
        Set the file name for capturing on the iPhone server.

        Args:
        - gloss: The gloss to be set as the file name.

        Description:
        This method sets the file name for capturing on the iPhone server.
        It also resets the capture number.
        """
        print("Setting filename to: ", gloss)
        print("ARGS: ", args)
        self.toIphone.send_message("/Slate", [self.gloss])

        # Don't reset the take number if the gloss is the same
        if self.gloss == gloss:
            return

        self.gloss = gloss
        self.takenumber = 0
    
    def request_battery(self, *args):
        """
        Request battery information from the iPhone server.

        Description:
        This method sends a message to the iPhone server to request battery information.
        """
        self.toIphone.send_message("/BatteryQuery", [])

    def save_file(self, command, timecode, blendshapeCSV, referenceMOV, *args):
        """
        Save a file on the iPhone server.

        Args:
        - timecode: Timecode information.
        - blendshapeCSV: Blendshape CSV data.
        - referenceMOV: Reference MOV file.

        Description:
        This method sends a transport message to the iPhone server to save a file.
        """
        print(f"send the transport towards:\tCSV{self.args.target_ip}:{str(self.args.receive_csv_port)}\tMOV{self.args.target_ip}:{str(self.args.receive_video_port)}")
        self.toIphone.send_message("/Transport", [self.args.target_ip + ':' + str(self.args.receive_csv_port), blendshapeCSV])
        self.toIphone.send_message("/Transport", [self.args.target_ip + ':' + str(self.args.receive_video_port), referenceMOV])

class LiveLinkFaceServer: 
    """
    Class LiveLinkFaceServer launches the live link server that communicates with the iPhone.

    Description:
    The IP used in this server should be the same as the listener in the iPhone.
    The server is NOT launched asynchronously, but it contains the client object to do any communication
    to the iPhone where necessary.
    The server is a man in the middle for all the communication with the iPhone, including setting up the
    TCP connection for the file transfer.
    """
    def __init__(self, gloss, args):
        """
        Initialize the LiveLinkFaceServer.

        Args:
        - gloss: The gloss for capturing.
        - args: The arguments containing necessary configurations.

        Description:
        This method initializes the LiveLinkFaceServer instance. It sets up the dispatcher for handling
        incoming messages, initializes the client object, and sets up rules for message handling.
        """
        self.gloss = gloss
        self.args = args
        self.client = LiveLinkFaceClient(args, gloss)

        # Start server rules here, add a default rule for all other incoming messages
        self.dispatcher = Dispatcher()
        self.dispatcher.map("/OSCSetSendTargetConfirm", print)
        self.dispatcher.map("/QuitServer", self.quit_server)

        # Start client requests here
        self.dispatcher.map("/BatteryQuery", self.client.request_battery)
        self.dispatcher.map("/SetFileName", lambda address, *args: self.client.set_filename(*args))
        self.dispatcher.map("/RecordStart", self.start_recording)
        self.dispatcher.map("/RecordStop", self.client.stop_capture)
        # When the recording is fully finished, instruct the client to save the file locally
        self.dispatcher.map("/RecordStopConfirm", self.client.save_file)

        # Start TCP requests here
        self.dispatcher.map("/CloseTCPListener", self.send_close_tcp)
        self.dispatcher.map("/SendFileNameToTCP", self.send_file_name_tcp)
        self.dispatcher.map("/Alive", self.ping_back)

        # What to do with unknown messages
        self.dispatcher.set_default_handler(self.default)

    def init_server(self):
        """
        Start the server.

        Description:
        This method starts the server to receive messages from the iPhone.
        """
        print("Receiving On: ", self.args.target_ip, self.args.target_port)
        self.server = BlockingOSCUDPServer((self.args.target_ip, self.args.target_port), self.dispatcher)
        self.server.serve_forever()

    def quit_server(self, *args):
        """
        Exit the server.

        Description:
        This method exits the server and client through the /QuitServer handle.
        """
        sys.exit()

    def start_recording(self, *args):
        """
        Start recording with the iPhone.

        Description:
        This method starts recording with the iPhone and starts accepting a file with the TCP socket.
        """
        self.client.start_capture()
        self.send_signal_recording_tcp()

    def send_basic_cmd_tcp(self, cmd, extra="", port=None, *args):
        """
        Send a basic command to the TCP socket.

        Args:
        - cmd: The command to be sent.
        - extra: Additional information to be sent.

        Description:
        This method sends a basic message containing a command to the TCP socket.
        """
        if port is None:
            port = self.args.receive_csv_port

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.args.target_ip, port))

            # Send the recording message
            close_message = "COMMAND:" + cmd + "!" + extra
            client_socket.sendall(struct.pack('>I', len(close_message)))
            client_socket.sendall(close_message.encode())

    def send_close_tcp(self, *args):
        """
        Ask the TCP socket to close itself.

        Description:
        This method asks the TCP socket to close itself.
        """
        self.send_basic_cmd_tcp('CLOSE', port=self.args.receive_csv_port)
        self.send_basic_cmd_tcp('CLOSE', port=self.args.receive_video_port)

    def send_file_name_tcp(self, addr, file_name, *args):
        """
        Send a file name to the TCP socket.

        Args:
        - addr: The address.
        - file_name: The name of the file to be sent.

        Description:
        This method sends the TCP socket a file name.
        """
        self.send_basic_cmd_tcp('FILE', file_name)
        self.send_basic_cmd_tcp('FILE', file_name, port=self.args.receive_video_port)

    def send_are_you_okay_tcp(self, *args):
        """
        Ask the TCP socket if it is okay.

        Description:
        This method asks the TCP socket if it is okay.
        """
        self.send_basic_cmd_tcp('ALIVE')
        self.send_basic_cmd_tcp('ALIVE', port=self.args.receive_video_port)

    def send_signal_recording_tcp(self, *args):
        """
        Set the TCP socket to "file receiving" mode.

        Description:
        This method sets the TCP socket to the "file receiving" mode.
        """
        self.send_basic_cmd_tcp('RECORD')
        self.send_basic_cmd_tcp('RECORD', port=self.args.receive_video_port)

    def ping_back(self, *args):
        """
        Respond to requests, indicating that the OSC server is alive.

        Description:
        This method responds to requests, indicating that the OSC server is alive.
        """
        print("OSC SERVER ALIVE")
        self.send_are_you_okay_tcp()

    def default(self, address, *args):
        """
        Print all messages by default.

        Args:
        - address: The address that we receive the message from.
        - args: Additional arguments.

        Description:
        This method prints all messages by default.
        """
        print(f"{address}: {args}")
