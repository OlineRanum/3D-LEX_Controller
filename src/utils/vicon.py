import sys
sys.path.append(r"C:\Program Files\Vicon\ShogunLive1.13\SDK\Python")

try:
    from shogun_live_api.interfaces.capture_services import CaptureServices
    from vicon_core_api.client import Client, RPCError
except ImportError as e:
    print(f"ImportError: {str(e)}")
    sys.exit(1)

# from vicon_core_api import *
# from shogun_live_api import *

class ShogunClient:
    def __init__(self, args, filename):
        shogunLiveClient = Client(args["shogun_hostname"])
        self.capture = CaptureServices(shogunLiveClient)
        
        # Test the connection by fetching the capture folder
        try:
            capture_folder = self.capture.capture_folder()
            print(f"Connected to Shogun. Capture Folder: {capture_folder}")
        except RPCError as e:
            print(f"Failed to connect to Shogun: {e}")

        self.set_filename(filename)

        # self.list_available_methods()

    def list_available_methods(self):
        # Using dir() to list all methods and attributes
        methods = dir(self.capture)
        print("Available Methods in CaptureServices:")
        for method in methods:
            print(method)

    def set_filename(self, filename):
        try:
            self.capture.set_capture_name(filename)
            print(f"Capture name set to {filename}")
        except RPCError as e:
            print(f"Failed to set capture name: {e}")

    def start_capture(self):    
        self.capture.start_capture()

    def stop_capture(self):
        self.capture.set_capture()
    
    def save_capture(self, filename):
        # TODO: talk to Jari about this 
        # Does shogun save at a specific location 
        # Do we just move it 
        raise NotImplementedError

# Example usage
args = {
    "shogun_hostname": "localhost"
}
shogun = ShogunClient(args, "test_capture")
