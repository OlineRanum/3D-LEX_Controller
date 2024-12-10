import os
import subprocess
import datetime
import platform
import re
import time
import asyncio
from threading import Thread

class FFmpegRecorder:
    def __init__(self, save_path="./", file_name="recording", video_device="video=UT-VID 00K0626579", audio_device="audio=Digital Audio Interface (UT-AUD 00K0626579)", popUp=None):
        self.save_path = save_path
        self.file_name = file_name
        self.video_device = video_device
        self.audio_device = audio_device
        self.recording = False
        self.ffmpeg_process = None  # This will store the subprocess handle
        self.current_output_file = None
        self.popup = popUp

    def set_save_location(self, path, date_folder=True):
        """Sets the location to save the recorded files."""
        if not os.path.exists(path):
            raise ValueError(f"Path '{path}' does not exist.")
        
        if date_folder:
            path = os.path.join(path, datetime.datetime.now().strftime("%Y-%m-%d"))
            os.makedirs(path, exist_ok=True)

        self.save_path = path
        print(f"[ffmpeg] Save path set to: {self.save_path}")

    def check_last_file(self):
        """Check the last recorded file and if it is saved. If not print a warning."""
        if not os.path.exists(self.current_output_file):
            print(f"[ffmpeg WARNING] Last recorded file '{self.current_output_file}' not found.")

        # Use ffprobe to get the duration of the video
        try:
            command = [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", self.current_output_file
            ]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            duration = float(result.stdout.strip())
        except Exception as e:
            print(f"[ffmpeg WARNING] Unable to determine duration of '{self.current_output_file}': {e}")
            return

        # Get the file size in MB
        file_size_mb = os.path.getsize(self.current_output_file) / (1024 * 1024)

        # Expected file size (in MB) based on duration (adjust 2.0 for your average file size per second)
        avg_size_per_sec = 0.470  # Based on a 1080p 60 FPS video with 5000 kbps bitrate that we have recorded over 22 seconds
        expected_size_mb = duration * avg_size_per_sec

        # Set a tolerance threshold (e.g., 20% smaller than expected)
        tolerance_factor = 0.8
        if file_size_mb < expected_size_mb * tolerance_factor:
            warning_message = (
                f"[ffmpeg WARNING] File '{self.current_output_file}' might be invalid: "
                f"size is {file_size_mb:.2f} MB, expected at least {expected_size_mb * tolerance_factor:.2f} MB."
            )
            print(warning_message)
            if self.popup is not None:
                self.popup.show_popup("File Size Warning", warning_message)
        else:
            print(f"[ffmpeg INFO] File '{self.current_output_file}' appears valid: {file_size_mb:.2f} MB.")


    def get_unique_filename(self):
        """Generates a unique file name by appending a number if the file already exists."""
        base_name = self.file_name
        file_extension = ".mp4"
        counter = 1

        if not os.path.exists(os.path.join(self.save_path, f"{base_name}{file_extension}")):
            return f"{base_name}{file_extension}"

        # Generate the unique file name
        while os.path.exists(os.path.join(self.save_path, f"{base_name}_{counter}{file_extension}")):
            counter += 1
        
        return f"{base_name}_{counter}{file_extension}"

    def set_recording_name(self, name):
        """Sets the name of the recording file."""
        print(f"[ffmpeg] Recording name set to: {name}")
        self.file_name = name

    def list_devices(self):
        """List available audio and video devices using FFmpeg."""
        if platform.system() != "Windows":
            print("[ffmpeg] Device listing is only supported on Windows. Returning empty list.")
            return {'audio': [], 'video': []}

        # Command to list devices
        command = ['ffmpeg', '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy']
        
        try:
            # Run the command and capture stderr (device list is printed to stderr)
            result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
            output = result.stderr
        except FileNotFoundError:
            print("[ffmpeg ERROR] FFmpeg not found. Make sure it's installed and in your PATH.")
            return {'audio': [], 'video': []}

        # Parse devices from the FFmpeg output
        audio_devices, video_devices = [], []
        current_section = None

        for line in output.splitlines():
            line = line.strip()
            if "DirectShow audio devices" in line or "(audio)" in line:
                current_section = 'audio'
            elif "DirectShow video devices" in line or "(video)" in line:
                current_section = 'video'
            
            if line.startswith('[dshow @') and '"' in line:
                # Extract device name inside quotes
                match = re.search(r'"([^"]+)"', line)
                if match:
                    device_name = match.group(1)
                    if current_section == 'audio':
                        audio_devices.append(device_name)
                    elif current_section == 'video':
                        video_devices.append(device_name)
        
        return {'audio': audio_devices, 'video': video_devices}

    def validate_devices(self, given_audio_device=None, given_video_device=None):
        if given_audio_device is None:
            given_audio_device = self.audio_device
        if given_video_device is None:
            given_video_device = self.video_device

        # Retrieve available devices
        devices = self.list_devices()
        audio_devices = devices['audio']
        video_devices = devices['video']

        # Validate audio device
        if given_audio_device not in audio_devices:
            print(f"[ffmpeg ERROR] Audio device '{given_audio_device}' not found. Available devices: {audio_devices}")
            return False

        # Validate video device
        if given_video_device not in video_devices:
            print(f"[ffmpeg ERROR] Video device '{given_video_device}' not found. Available devices: {video_devices}")
            return False
        
        print(f"[ffmpeg] Both {given_video_device} and {given_audio_device} are valid.")
        return True

    def start_record(self):
        """Start the FFmpeg recording using the given devices."""
        if self.recording:
            print("[ffmpeg] Recorder already recording! Stopping the current recording, then starting a new one.")
            # TODO FIX THE STOPPING OF THE RECORDING LOOP
            self.popup.show_popup("Recording Warning", "RESTART THE PROGRAM, recorder is stuck in loop")

        # Build the output file path
        output_file = os.path.join(self.save_path, self.get_unique_filename())
        
        # Construct the FFmpeg command
        command = [
            'ffmpeg',
            '-f', 'dshow',
            '-i', f'video={self.video_device}:audio={self.audio_device}',  # Input devices
            '-vf', 'format=yuv420p',  # Set pixel format
            '-s', '1920x1080',        # Set resolution to 1080p
            '-r', '60',               # Set frame rate to 60 FPS
            '-preset', 'fast',        # Encoding preset
            '-y',                     # Overwrite output file if it exists
            '-b:v', '5000k',          # Lower video bitrate
            '-shortest',              # Stop recording when the shortest stream ends (video/audio)
            output_file               # Output file path
        ]

        # Start the FFmpeg process and save the process handle
        print(f"[ffmpeg] Recording started: {output_file}")
        self.recording = True
        self.current_output_file = output_file
        # self.ffmpeg_process = subprocess.Popen(command, stdin=subprocess.PIPE, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        self.ffmpeg_process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
    def stop_record(self):
        """Stop the FFmpeg recording."""
        if not self.recording:
            print("[ffmpeg] No recording in progress.")
            return False

        print("[ffmpeg] Stopping the optical camera...")
        # await asyncio.sleep(0.5) # Wait for half a second before stopping the recording, making sure we have the last frames

        # Start stopping FFmpeg in a separate thread
        thread = Thread(target=self.stop_ffmpeg, args=(self.ffmpeg_process,))
        thread.start()

        self.ffmpeg_process = None
        return True

    def stop_ffmpeg(self, ffmpeg_process):
        """This function will run in a separate thread to stop FFmpeg."""
        try:
            # Perform the blocking FFmpeg operations
            ffmpeg_process.communicate(str.encode("q"))  # Send a 'q' to stop
            ffmpeg_process.wait()  # Wait for FFmpeg to finish
            # self.ffmpeg_process.terminate()  # Terminate the FFmpeg process
        except Exception as e:
            print(f"[ffmpeg] Error while stopping FFmpeg: {e}")
        finally:
            ffmpeg_process = None
            self.check_last_file()
            # After stopping FFmpeg, do the final cleanup
            print("[ffmpeg] Recording and processing stopped.")
            self.recording = False
            self.current_output_file = None

    # def _stop_ffmpeg_in_thread(self):
    #     """Run the blocking FFmpeg stop operations in a separate thread."""
    #     loop = asyncio.get_event_loop()

    #     def stop_ffmpeg():
    #         """This function will run in a separate thread to stop FFmpeg."""
    #         try:
    #             # Perform the blocking FFmpeg operations
    #             self.ffmpeg_process.communicate(str.encode("q"))  # Send a 'q' to stop
    #             self.ffmpeg_process.wait()  # Wait for FFmpeg to finish
    #             self.ffmpeg_process.terminate()  # Terminate the FFmpeg process
    #         except Exception as e:
    #             print(f"[ffmpeg] Error while stopping FFmpeg: {e}")
    #         finally:
    #             self.ffmpeg_process = None

    #         # Once FFmpeg stops, call back to the event loop to handle cleanup
    #         loop.call_soon_threadsafe(self._on_ffmpeg_stopped)

    #     # Start the FFmpeg stop process in a separate thread
    #     threading.Thread(target=stop_ffmpeg, daemon=True).start()

    # def _on_ffmpeg_stopped(self):
    #     """Callback after FFmpeg has stopped."""
    #     self.check_last_file()

    def __del__(self):
        """Ensure that FFmpeg is stopped when the object is deleted."""
        if self.recording:
            self.stop_record()


# # Usage Example
# if __name__ == "__main__":
#     recorder = FFmpegRecorder(save_path="./", file_name="test_recording", video_device="UT-VID 00K0626579", audio_device="Digital Audio Interface (UT-AUD 00K0626579)")
#     recorder.set_save_location('D:\\VideoCapture')  # Set your desired save location
#     recorder.set_recording_name("OCHTEND-D_241209_4")

#     # List devices (optional, useful for discovering available devices)
#     # recorder.list_devices()

#     recorder.start_record()
#     time.sleep(5)  # Simulate 5 seconds of recording
#     recorder.stop_record()
