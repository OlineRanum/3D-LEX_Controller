from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from asyncio import run 
import os 
from pythonosc.osc_server import BlockingOSCUDPServer
import sys

# Class LiveLinkFaceClient sends messages to the live link server on the IPhone
# Sometimes it will be requested to save the file by the python server, and other times
# it will be requested to send messages by the IO
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
        # self.save_file()

    def set_filename(self, gloss, *args):
        self.gloss = gloss
        self.toIphone.send_message("/Slate", [self.gloss])
        self.takenumber = 0
    
    def request_battery(self, *args):
        self.toIphone.send_message("/BatteryQuery", [])

    def save_file(self, timecode, blendshapeCSV, referenceMOV, *args):
        print("send the transport towards - " + self.args.target_ip + ':' + str(self.args.target_port))
        print(timecode, blendshapeCSV, referenceMOV, *args)
        # Ask our client to send a transport message to our server 
        self.toIphone.send_message("/Transport", [self.args.target_ip + ':' + str(self.args.target_port), referenceMOV])

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
        self.dispatcher.map("/QuitServer", self.quitServer)

        # Start client requests here
        self.dispatcher.map("/SetFileName", self.client.set_filename)
        self.dispatcher.map("/RecordStart", self.client.start_capture)
        self.dispatcher.map("/RecordStop", self.client.stop_capture)
        # When the recording is fully finished, instruct the client to save the file locally
        self.dispatcher.map("/RecordStopConfirm", self.client.save_file)

        self.dispatcher.set_default_handler(self.default)


    # Server launch code, serving on target ip and port
    def init_server(self):
        print("Receiving On: ", self.args.target_ip, self.args.target_port)
        self.server = BlockingOSCUDPServer((self.args.target_ip, self.args.target_port), self.dispatcher)
        self.server.serve_forever()

    # Server functions start here
    def requestClientSaveFile(self, timecode, blendshapeCSV, referenceMOV, *args):
        self.client.save_file(timecode, blendshapeCSV, referenceMOV, args)

    # Exit the server and client through the /QuitServer handle
    def quitServer(self, *args):
        sys.exit()
    
    def requestClientRecordStart(self, *args):
        self.client.start_capture()
            
    def requestClientRecordStop(self, *args):
        self.client.stop_capture()

    # Print all messages by default
    def default(self, address, *args):
        print(f"{address}: {args}")
