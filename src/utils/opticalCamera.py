import os
import subprocess
import datetime
import platform
import re
import time

class FFmpegRecorder:
    def __init__(self, save_path="./", file_name="recording", video_device="video=UT-VID 00K0626579", audio_device="audio=Digital Audio Interface (UT-AUD 00K0626579)"):
        self.save_path = save_path
        self.file_name = file_name
        self.video_device = video_device
        self.audio_device = audio_device
        self.recording = False
        self.ffmpeg_process = None  # This will store the subprocess handle

    def set_save_location(self, path, date_folder=True):
        """Sets the location to save the recorded files."""
        if not os.path.exists(path):
            raise ValueError(f"Path '{path}' does not exist.")
        
        if date_folder:
            path = os.path.join(path, datetime.datetime.now().strftime("%Y-%m-%d"))
            os.makedirs(path, exist_ok=True)

        self.save_path = path
        print(f"[ffmpeg] Save path set to: {self.save_path}")

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
            print("[ffmpeg] Recorder already recording!")
            return

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
            '-b:v', '5000k',          # Set video bitrate to 5000k (adjust according to your needs)
            '-shortest',              # Stop recording when the shortest stream ends (video/audio)
            output_file               # Output file path
        ]

        # Start the FFmpeg process and save the process handle
        print(f"[ffmpeg] Recording started: {output_file}")
        self.recording = True
        # self.ffmpeg_process = subprocess.Popen(command, stdin=subprocess.PIPE, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        self.ffmpeg_process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
    def stop_record(self):
        """Stop the FFmpeg recording."""
        if not self.recording:
            print("[ffmpeg] No recording in progress.")
            return

        time.sleep(1) # Wait for a second before stopping the recording, making sure we have the last frames
        self.ffmpeg_process.communicate(str.encode("q")) #Equivalent to send a Q
        self.ffmpeg_process.wait() #Wait for the process to finish
        self.ffmpeg_process.terminate() #Terminate the process
        self.ffmpeg_process = None

        # Stop the FFmpeg process
        print("[ffmpeg] Recording and processing stopped.")
        self.recording = False

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
