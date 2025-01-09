from src.config.setup import SetUp
import src.utils.obsRecording as obsRecording
import src.utils.popUp as popUp

if __name__ == '__main__':
    args = SetUp("config.yaml")
    obs = obsRecording.OBSController(args.obs_host, args.obs_port, args.obs_password, popUp=popUp.PopUp())
    
    if obs.statusCode == obsRecording.OBSStatus.NOT_CONNECTED or obs.statusCode == obsRecording.OBSStatus.ERROR:
        print("OBS not connected or turned off. Please check the connection and try again.")
        exit()

    try:
        obs.set_save_location(args.obs_save_folder, gloss_name="testb")
        obs.set_buffer_folder(args.obs_buffer_folder)

        # Start recording for each scene (one at a time for simplicity)
        obs.start_recording()

        # Simulate recording duration
        import time
        print("Recording for 5 seconds...")
        time.sleep(15)

        # Stop recording
        obs.stop_recording()

    finally:
        obs.disconnect()
