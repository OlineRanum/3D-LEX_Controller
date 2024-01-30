from pythonosc.udp_client import SimpleUDPClient
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher


class LiveLinkFaceClient:
    def __init__(self, args, gloss):
        self.client = SimpleUDPClient(args.llf_udp_ip, args.llf_udp_port)
        self.client.send_message("/OSCSetSendTarget", [args.llf_ip, args.llf_port])
        self.client.send_message("/VideoDisplayOff", [])

        # Set gloss of first sign
        self.set_filename(gloss)
    
    def start_capture(self):
        self.client.send_message("/RecordStart", ["Calibratie", 3])
    
    def stop_capture(self):
        self.client.send_message("/RecordStop", [])

    def set_filename(self, gloss):
        self.client.send_message("/Slate", [gloss])
    


class LiveLinkFaceServer:
    def __init__(self, args):
        self.dispatcher = Dispatcher()
        self.dispatcher.map("/filter", print)
        self.dispatcher.map("/OSCSetSendTargetConfirm", print)
        self.dispatcher.map("/volume", self.print_volume_handler, "Volume")

        self.server = osc_server.ThreadingOSCUDPServer(
            (args.target_ip, args.target_port), self.dispatcher)

        print("Serving on {}".format(self.server.server_address))
        self.server.server_forever()

    def print_volume_handler(self, unused_addr, args, volume):
        print("[{0}] ~ {1}".format(args[0], volume))
    
    def print_compute_handler(self, unused_addr, args, volume):
        try:
            print("[{0}] ~ {1}".format(args[0], args[1](volume)))
        except ValueError:
            pass
    
    def export_capture(self, gloss):
        raise NotImplementedError