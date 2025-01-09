import time
import os
import shutil
from datetime import datetime
import obsws_python as obs
import popUp as popUp

# OBS WebSocket connection details
HOST = 'localhost'
PORT = 4457
PASSWORD = None

class OBSController:
    def __init__(self, host, port, password):
        print("Initializing OBS Controller...")
        self.host = host
        self.port = port
        self.password = password
        self.buffer_folder = r"D:\VideoCapture\SourceRecordBuffer"
        self.last_gloss_name = None

        self.check_connection()
        self.ws = None  # Initialize the client without parameters
        self.connect()

    def set_buffer_folder(self, folder_path):
        self.buffer_folder = folder_path

    def check_connection(self):
        import websocket

        try:
            ws = websocket.create_connection(f"ws://{self.host}:{self.port}")
            print("Should be able to connect to OBS webserver!")
            ws.close()
        except Exception as e:
            print(f"You cannot connect to the OBS webserver: {e}")

    def connect(self):
        try:
            if self.password:
                self.ws = obs.ReqClient(host=self.host, port=self.port, password=self.password)
            else:
                self.ws = obs.ReqClient(host=self.host, port=self.port)
            print("Connected to OBS WebSocket.")
        except Exception as e:
            print(f"Failed to connect to OBS: {e}")

    def list_methods(self):
        # Print available methods/attributes of the ReqClient object
        print(dir(self.ws))

    def set_save_location(self, root_folder, gloss_name="Recording"):
        """Sets the location to save the recorded files dynamically with incremental folders."""
        if not os.path.exists(root_folder):
            # Pop up a warning if the folder does not exist, and ask the user if they want to create it
            popup = popUp.PopUp()
            create = popup.show_popup_yesno("Warning", f"The folder '{root_folder}' does not exist. Do you want to create it?")
            if not create:
                raise ValueError(f"Root path '{root_folder}' does not exist.")
            else:
                os.makedirs(root_folder, exist_ok=True)

        self.last_gloss_name = gloss_name

        # Create a date folder under the root folder
        date_folder = os.path.join(root_folder, datetime.now().strftime("%Y-%m-%d"))
        os.makedirs(date_folder, exist_ok=True)

        # Create a subfolder for each recording session with incremental numbers
        session_folder_base = os.path.join(date_folder, gloss_name)
        session_folder = self.get_incremental_folder(session_folder_base)

        os.makedirs(session_folder, exist_ok=True)

        self.save_path = session_folder
        self.last_used_folder = self.save_path
        print(f"[OBS] Save path set to: {self.save_path}")

        # Optionally: Set OBS's recording directory to this path
        self.set_record_directory(self.save_path)

    def get_incremental_folder(self, base_path):
        """Finds the next available subfolder number in the given base path."""
        i = 1
        while os.path.exists(os.path.join(base_path, f"{i}")):
            i += 1
        return os.path.join(base_path, f"{i}")

    def set_record_directory(self, path):
        """Sets OBS's recording directory using the WebSocket API."""
        try:
            self.ws.set_record_directory(path)
            print(f"[OBS] Recording directory set to: {path}")
        except Exception as e:
            print(f"Failed to set recording directory in OBS: {e}")

    def move_recorded_files(self, max_retries=3, delay=0.5):
        """Move all files from the buffer to the last used folder with retries on failure."""
        if not self.last_used_folder:
            print("No folder set for the recording. Can't move the files.")
            return
        
        # Iterate over all files in the SourceRecordBuffer folder
        try:
            for filename in os.listdir(self.buffer_folder):
                file_path = os.path.join(self.buffer_folder, filename)
                if os.path.isfile(file_path):
                    destination = os.path.join(self.last_used_folder, filename)
                    retries = 0
                    while retries < max_retries:
                        try:
                            shutil.move(file_path, destination)
                            print(f"Moved {filename} to {self.last_used_folder}")
                            break
                        except PermissionError as e:
                            print(f"Error moving {filename}: {e}. Retrying in {delay} seconds...")
                            retries += 1
                            time.sleep(delay)
                            if retries == max_retries:
                                print(f"Failed to move {filename} after {max_retries} retries.")
        except Exception as e:
            print(f"Failed to move the files: {e}")

    def prepend_gloss_name_last_recordings(self, gloss_name=None):
        """Prepend the gloss name to the last recorded files."""
        if not self.last_used_folder:
            print("No folder set for the recording. Can't prepend the gloss name.")
            return
        
        if not gloss_name:
            gloss_name = self.last_gloss_name

        try:
            for filename in os.listdir(self.last_used_folder):
                file_path = os.path.join(self.last_used_folder, filename)
                if os.path.isfile(file_path):
                    new_filename = f"{gloss_name}_{filename}"
                    os.rename(file_path, os.path.join(self.last_used_folder, new_filename))
                    print(f"Renamed {filename} to {new_filename}")
        except Exception as e:
            print(f"Failed to rename the files: {e}")

    def disconnect(self):
        self.ws.disconnect()
        print("Disconnected from OBS WebSocket.")

    def start_recording(self):
        try:
            self.ws.start_record()
            print("Started recording.")
        except Exception as e:
            print(f"Failed to start recording: {e}")

    def stop_recording(self):
        try:
            self.ws.stop_record()
            print("Stopped recording.")
            self.move_recorded_files()
            self.prepend_gloss_name_last_recordings()
        except Exception as e:
            print(f"Failed to stop recording: {e}")


# Example usage
if __name__ == '__main__':
    obs = OBSController(HOST, PORT, PASSWORD)

    try:
        obs.set_save_location(r"D:\VideoCapture\testingOBSRecordScript", gloss_name="gloss2")

        # Start recording for each scene (one at a time for simplicity)
        obs.start_recording()

        # Simulate recording duration
        import time
        print("Recording for 5 seconds...")
        time.sleep(5)

        # Stop recording
        obs.stop_recording()

    finally:
        obs.disconnect()
