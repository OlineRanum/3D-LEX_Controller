🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍
# The 3🍍-LEX Control System 
🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍


The README for the 3🍍-LEX Control System repository is structured to provide practical guidance on managing data acquisition pipelines. It covers essential topics such as launching servers in a Windows environment, WebSocket communication, OSC server handles/functions, TCP socket communication, and includes helpful pipeline illustrations. Each section offers straightforward instructions and insights, making it easier for developers, researchers, and enthusiasts to understand and utilize the system effectively.

### Project Hardware
- Vicon Vero Cameras: Utilized for motion capture purposes.
- StretchSense Gloves: Employed for hand motion tracking.
- iPhone: Used as a device for communication and potentially for additional data input.

### External Software
In addition to our custom scripts, the project relies on the following software tools:
- Shogun Live: Integrated for motion capture and potentially for controlling the Hand Engine.
- Hand Engine: Directly controlled through Shogun Live, likely used for hand motion analysis.
- Live Link Face: Utilized for facial motion capture and communication.

### External Software Communication summary:
- Shogun API: Used to communicate with Shogun Live, facilitating control and data exchange.
- Live Link Face OSC Protocol: Employed to communicate with Live Link Face, enabling data transfer and synchronization.
- Hand Engine Integration: Coordinated through Shogun Live, suggesting potential integration with the overall motion capture system.

### Usage in Windows
In windows, double click the job.bat script to launch all servers simultaneously. Communicate with the system by using the websocket.

---

## Recording with Optical Cameras through OBS
The OBS portion of the program allows us to record with optical cameras through OBS. This section goes over prerequisites and steps to properly setup OBS.

### Prerequisites
- **OBS Version**: 26.0 or higher
- **OBS Source Record Plugin**: [Download here](https://obsproject.com/forum/resources/source-record.1285/)

### Setup Instructions

#### Step 1: Enable WebSocket Server in OBS
1. Open OBS settings.
2. Go to the **WebSocket Server Settings** section (requires OBS WebSocket plugin).
3. Enable the WebSocket server and note the following:
   - **Host** (default: `localhost`)
   - **Port** (default: `4444`)
   - **Password** (if required).


#### Step 2: Configure OBS Scenes and Cameras
1. **Create Scenes**:
   - Add a scene for each camera you want to record.
2. **Add Cameras**:
   - For each scene, add the corresponding camera as a source.
3. **Configure Source Record Plugin**:
   - For all cameras **except the main camera**:
     1. Go to the scene.
     2. Add a **Source Record** filter to the camera source.
     3. Set the **Record Mode** to `Recording`.
     4. Specify the path to a `buffer_folder` (default: `D:/VideoCapture/SourceRecordBuffer`).
     5. Modify the default file name to ensure it doesn’t collide with other cameras' recordings.
     6. (Optional) If you want file splitting based on recording time or size, you can set this here.


#### Step 3: Select the Main Camera
- During a recording session, ensure the **main camera scene** is selected in OBS. 
  - This camera will record directly through OBS.
  - Other cameras will record via the Source Record plugin.
  - (Optional) In the advanced output settings, under record, you can set automatic file splitting if needed.


#### Step 4: Update the Configuration File
In your `config.yaml`, set the following parameters:
- `obs_host`: Host address of the OBS WebSocket server.
- `obs_port`: Port for the OBS WebSocket server.
- `obs_buffer_folder`: Path to the folder used by the Source Record plugin for buffer recordings.
- `obs_save_folder`: Path to the folder where final recordings will be saved.


### Recording Workflow

#### Python Commands
Once the setup is complete, you can control the recording via Python using the following commands:

```python
# Initialize OBS Controller
obs = obsRecording.OBSController(args.obs_host, args.obs_port, args.obs_password, popUp=popUp.PopUp())

# Set Save Location
obs.set_save_location(args.obs_save_folder, gloss_name="testName")

# Set Buffer Folder location (should match the filter location of the Source Record plugin)
obs.set_buffer_folder(args.obs_buffer_folder)

# Start Recording
obs.start_recording()

# Stop Recording
obs.stop_recording()
```

---

# How to use the websocket
The websocket (in mainController.py) serves as the communication with all the devices in this project. It calls the controlAPI.py API to do so. But how do we communicate with the websocket? Connect to the correct port and use the following messages (each message begins with the function call and then some data):
```
await websocket.send("greet:Hello, Server!")
await websocket.send("fileName:TestFileName")
await websocket.send("ping:a")
await websocket.send("recordStart:starting the recording")
await websocket.send("recordStop:stopping the recording")
await websocket.send("close:a")
```


# handles / functions for the OSC server
In order to communicate with the OSC server, we use handles. The following handles are defined:
- "/QuitServer", quits the server and closes the python script
- "/SetFileName", takes a _gloss_ and sets the filename to the gloss name
- "/RecordStart", requests the IPhone to start capturing
-  "/RecordStop", requests the IPhone to stop capturing (IPhone should respond with "/RecordStopConfirm", which triggers the saving algorithm)
- "/BatteryQuery", requests the battery value of the IPhone and outputs it to the terminal
- "/*", everything else will be printed in the terminal

# TCP socket communication
The socket operates in a single state, handling incoming messages based on their content. The socket differentiates between commands and data as follows:

- **Commands**: Messages containing a '!' character are considered commands. These include:
  - **"FILE!<file_name>"**: Sets the file name for the incoming data.
  - **"RECORD!<message>"**: Indicates that the socket should start accepting data.
  - **"CLOSE!<message>"**: Closes the socket.
  - **"ALIVE!<message>"**: Prints a message to confirm the socket is active.
- **Data**: Messages without a '!' character or messages with a '!' character but no matching command are treated as file data. These are saved to a file in the specified directory.

### Default File Naming
If a file name is not specified using the "FILE" command, the data will be saved with the default name "NoFileNameGiven". Subsequent recordings will append "_rerecorded" to the file name.

# Pipeline Illustrations
Needs to be updated (missing Shogun Post and OBS)
![Pipeline](/img/PipelineSignbankProject2.png)

