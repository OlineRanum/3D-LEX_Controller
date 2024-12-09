import os
import subprocess
import datetime
import platform
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
        print(f"Save path set to: {self.save_path}")

    def get_unique_filename(self):
        """Generates a unique file name by appending a number if the file already exists."""
        base_name = self.file_name
        file_extension = ".mp4"
        counter = 1
        # Generate the unique file name
        while os.path.exists(os.path.join(self.save_path, f"{base_name}_{counter}{file_extension}")):
            counter += 1
        return f"{base_name}_{counter}{file_extension}"

    def set_recording_name(self, name):
        """Sets the name of the recording file."""
        self.file_name = name

    def list_devices(self):
        """List available devices using FFmpeg."""
        if platform.system() == "Windows":
            command = ['ffmpeg', '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy']
            subprocess.run(command)
        else:
            print("Device listing is only supported on Windows.")

    def start_record(self):
        """Start the FFmpeg recording using the given devices."""
        if self.recording:
            print("Already recording!")
            return

        # Build the output file path
        output_file = os.path.join(self.save_path, self.get_unique_filename())
        
        # Construct the FFmpeg command
        command = [
            'ffmpeg',
            '-f', 'dshow',  # DirectShow input
            '-i', f'video={self.video_device}:audio={self.audio_device}',  # Input devices
            '-vf', 'format=yuv420p',  # Video format
            '-preset', 'fast',  # Encoding preset
            '-y',  # Overwrite output file if it exists
            output_file  # Output file
        ]
        
        # Start the FFmpeg process and save the process handle
        print(f"Recording started: {output_file}")
        self.recording = True
        # self.ffmpeg_process = subprocess.Popen(command, stdin=subprocess.PIPE, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        self.ffmpeg_process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        
    def stop_record(self):
        """Stop the FFmpeg recording."""
        if not self.recording:
            print("No recording in progress.")
            return

        # Stop the FFmpeg process
        self.recording = False
        print("Recording stopped.")
        
        self.ffmpeg_process.communicate(str.encode("q")) #Equivalent to send a Q
        time.sleep(3) 
        self.ffmpeg_process.terminate() #Terminate the process
        self.ffmpeg_process = None

    def __del__(self):
        """Ensure that FFmpeg is stopped when the object is deleted."""
        if self.recording:
            self.stop_record()


# Usage Example
if __name__ == "__main__":
    recorder = FFmpegRecorder(save_path="./", file_name="test_recording", video_device="UT-VID 00K0626579", audio_device="Digital Audio Interface (UT-AUD 00K0626579)")
    recorder.set_save_location('D:\\VideoCapture')  # Set your desired save location
    recorder.set_recording_name("test_11")

    # List devices (optional, useful for discovering available devices)
    # recorder.list_devices()

    recorder.start_record()
    time.sleep(5)  # Simulate 5 seconds of recording
    recorder.stop_record()
