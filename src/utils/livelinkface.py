from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import sys
import socket
import struct

# Class LiveLinkFaceClient sends messages to the live link server on the IPhone
class LiveLinkFaceClient:
    # The init starts the client and sets the python server address on the IPhone
    def __init__(self, args, gloss):
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
        self.toIphone.send_message("/RecordStart", [self.gloss, self.takenumber])
        return self.takenumber

    def stop_capture(self, *args):
        self.toIphone.send_message("/RecordStop", [])
        self.takenumber += 1

    def set_filename(self, gloss, *args):
        self.gloss = gloss
        self.toIphone.send_message("/Slate", [self.gloss])
        self.takenumber = 0
    
    def request_battery(self, *args):
        self.toIphone.send_message("/BatteryQuery", [])

    # Ask our client to send a transport message to the IPhone, the IPhone will send data to the TCP socket
    def save_file(self, timecode, blendshapeCSV, referenceMOV, *args):
        print("send the transport towards - " + self.args.target_ip + ':' + str(self.args.target_port + 2))
        self.toIphone.send_message("/Transport", [self.args.target_ip + ':' + str(self.args.target_port + 2), referenceMOV])

# Class LiveLinkFaceServer launches the live link server that communicates with the IPhone
# The IP used in this server should be the same as the listener in the IPhone
# The server is NOT launched asynchronously, but it contains the client object to do any communication
# to the IPhone where necessary.
# The server is a man in the middle for all the communication with the IPhone, including setting up the
# TCP connection for the file transfer.
class LiveLinkFaceServer:
    def __init__(self, gloss, args):
        self.gloss = gloss
        self.args = args
        self.client = LiveLinkFaceClient(args, gloss)

        # Start server rules here, add a default rule for all other incoming messages
        self.dispatcher = Dispatcher()
        self.dispatcher.map("/OSCSetSendTargetConfirm", print)
        self.dispatcher.map("/QuitServer", self.quit_server)

        # Start client requests here
        self.dispatcher.map("/BatteryQuery", self.client.request_battery)
        self.dispatcher.map("/SetFileName", self.client.set_filename)
        self.dispatcher.map("/RecordStart", self.client.start_capture)
        self.dispatcher.map("/RecordStop", self.client.stop_capture)
        # When the recording is fully finished, instruct the client to save the file locally
        self.dispatcher.map("/RecordStopConfirm", self.client.save_file)

        # Start TCP requests here
        self.dispatcher.map("/CloseTCPListener", self.send_close_tcp)
        self.dispatcher.map("/SendFileNameToTCP", self.send_file_name_tcp)
        self.dispatcher.map("/Alive", self.ping_back)

        # What to do with unknown messages
        self.dispatcher.set_default_handler(self.default)

    # Server launch code, serving on target ip and port
    def init_server(self):
        print("Receiving On: ", self.args.target_ip, self.args.target_port)
        self.server = BlockingOSCUDPServer((self.args.target_ip, self.args.target_port), self.dispatcher)
        self.server.serve_forever()

    # Exit the server and client through the /QuitServer handle
    def quit_server(self, *args):
        sys.exit()

    # Ask the TCP socket to close itself
    def send_close_tcp(self, *args):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.args.target_ip, self.args.target_port + 2))

            # Send the close message
            close_message = "CLOSE!"
            client_socket.sendall(struct.pack('>I', len(close_message)))
            client_socket.sendall(close_message.encode())

    # Send the TCP socket a file name
    def send_file_name_tcp(self, addr, file_name, *args):
        print(f"{addr}, {file_name}, {args}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.args.target_ip, self.args.target_port + 2))

            # Send length of message and then contents
            message = file_name + "!"
            client_socket.sendall(struct.pack('>I', len(message)))
            client_socket.sendall(message.encode())

    # Ask the TCP socket if he is okay
    def send_are_you_okay_tcp(self, *args):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.args.target_ip, self.args.target_port + 2))

            # Send the close message
            close_message = "ALIVE!"
            client_socket.sendall(struct.pack('>I', len(close_message)))
            client_socket.sendall(close_message.encode())

    # Tell whoever is asking that we are okay
    def ping_back(self, *args):
        print("OSC SERVER ALIVE")
        self.send_are_you_okay_tcp()

    # Print all messages by default
    def default(self, address, *args):
        print(f"{address}: {args}")