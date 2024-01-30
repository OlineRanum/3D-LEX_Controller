from vicon_core_api import *
from shogun_live_api import *

class ViconClient:
    def __init__(self):
        shogunLiveClient = Client('localhost')
        self.capture = CaptureServices(shogunLiveClient)
        
        def set_filename(self, filename):
            self.capture.capture_name(filename)
            
        def start_capture(self):    
            self.capture.start_capture()

        def stop_capture(self):
            self.capture.set_capture()
            