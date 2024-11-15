import sys
sys.path.append(r"C:\Program Files\Vicon\ShogunLive1.13\SDK\Python\shogun_live_api")
sys.path.append(r"C:\Program Files\Vicon\ShogunLive1.13\SDK\Python\vicon_core_api")

# Import the shogun_live_api package
import shogun_live_api
import vicon_core_api
import time

# Now import CaptureServices correctly
from shogun_live_api.interfaces import CaptureServices as cap
from vicon_core_api.client import Client, RPCError

# List all attributes and modules within shogun_live_api
modules = dir(cap)
print(modules)
help(cap.capture_folder)

shogunLiveClient = Client('192.168.0.180')
print(shogunLiveClient.connected)

# shogunLiveClient.send_command("CaptureServices.CaptureFolder")
time.sleep(2)

capture = cap(shogunLiveClient)
print(dir(capture))
# Try to fetch the capture folder
try:
    # capture.set_capture_name("test_capture")
    capture_folder = capture.capture_folder()
    print(f"Capture folder: {capture_folder}")
except RPCError as e:
    print(f"RPCError occurred: {e}")
except Exception as ex:
    print(f"An unexpected error occurred: {ex}")

print("\n\n\n\n\n")

try:
    # Import the shogun_live_api package
    import shogun_live_api
    from shogun_live_api.interfaces import CaptureServices
    from vicon_core_api.client import Client, RPCError
except ImportError as e:
    print(f"ImportError: {str(e)}")
    sys.exit(1)

# from vicon_core_api import *
# from shogun_live_api import *

class ShogunClient:
    def __init__(self, args, filename):
        shogunLiveClient = Client(args["shogun_hostname"])
        # shogunLiveClient = Client(args["shogun_hostname"], args["shogun_port"])
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
    "shogun_hostname": "localhost",
    # "shogun_port": 37414,
}
shogun = ShogunClient(args, "test_capture")
