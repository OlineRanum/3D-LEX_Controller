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
The TCP socket can be communicated with. The socket has 2 states:
- Accepting commands
- Accepting data

The socket starts in the accepting commands state, and will move to the accepting data state when the command "RECORDING" is received. The socket moves from accepting data to accepting commands if _any_ message is received.
The commands can be sent through the OSC server functions and are as follows:
- "/CloseTCPListener", close the socket
- "/SendFileNameToTCP" [_file name here_], send a file name to the socket
- "/Alive", ask the socket to print something to the terminal

The RECORDING command is sent when we ask the OSC server to record through the "/RecordStart" handle.
Lastly, the data will be sent by the IPhone after the "/Transport" message has been sent to it.

# Pipeline Illustrations
![Pipeline](/img/PipelineSignbankProject2.png)

