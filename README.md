🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍
# The Pineapple Pipeline
🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍


The README for the Pineapple Piple repository is structured to provide practical guidance on managing data acquisition pipelines. It covers essential topics such as launching servers in a Windows environment, WebSocket communication, OSC server handles/functions, TCP socket communication, and includes helpful pipeline illustrations. Each section offers straightforward instructions and insights, making it easier for developers, researchers, and enthusiasts to understand and utilize the system effectively.

### Project Hardware
- Vicon System:
   - Vero Cameras: Utilized for motion capture purposes.
   - Flir Blackfly: Records video data.
   - Lock: Synchronizes Vicon Camera recordings.
- iPhone: Used as a device for communication, ARKit recordings of face animations and video.
- Razer KiyoPro: Records video data (can be replaced with any other webcam).

### External Software
In addition to our custom scripts, the project relies on the following software tools:
- Shogun Live: Integrated for motion capture.
- Shogun Post: Integrated for playing back motion capture data.
- Live Link Face: Utilized for facial motion capture and communication.
- OBS: Utilized for recording video data.

### External Software Communication summary:
- Shogun API: Used to communicate with Shogun Live, facilitating control and data exchange.
- Live Link Face OSC Protocol: Employed to communicate with Live Link Face, enabling data transfer and synchronization.
- OBS Websocket Server: Used to start and stop recordings within the OBS software.
   - OBS Source Record Plugin: Used to add extra cameras in OBS software.
 
### Usage in Windows
In windows, double click the job.bat script to launch all servers simultaneously. Communicate with the system by using the websocket. If Shogun Post is turned off, then it will be ignored (no playbacks of mocap data in the software).

---

## Recording with Optical Cameras through OBS
Make sure to include the submodule if you want to accomplish this:
```bash
git submodule update --init --recursive
```
The submodule comes from the following repo: https://github.com/J-Andersen-UvA/OBSRecorder

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

### Retargeted Animation Replay
- After recording, a replay of the retargeted animation is displayed on an avatar in Unreal Engine.
- This is achieved through a Blueprint event (a link to the blueprint will be added later).

# Pipeline Illustrations
![Pipeline](/img/PineapplePipelineLightVersion.png)

