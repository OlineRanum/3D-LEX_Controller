from vicon_core_api import *
from shogun_live_api import *

class ShogunClient:
    def __init__(self, args, filename):
        shogunLiveClient = Client(args.shogun_hostname)
        self.capture = CaptureServices(shogunLiveClient)

        self.set_filename(filename)
        
        def set_filename(self, filename):
            self.capture.capture_name(filename)
            
        def start_capture(self):    
            self.capture.start_capture()

        def stop_capture(self):
            self.capture.set_capture()
            