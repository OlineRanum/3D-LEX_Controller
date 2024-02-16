🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍
# 3🍍-LEX Control System 
🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍🍍
### Usage in Windows
In windows 10, double click the job.bat script to launch all servers simultaneously.

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
-  "/RecordStop", requests the IPhone to stop capturing (IPhone should respond with "/RecordStopConfirm", which triggers saving algorithm)
- "/BatteryQuery", requests the battery value of the IPhone and outputs it to the terminal
- "/*", everything else will be printed in the terminal

### TCP socket communication
The TCP socket can be communicated with. The socket has 2 states:
- Accepting commands
- Accepting data

The socket starts in the accepting commands state, and will move to the accepting data state when the command "RECORDING" is received. The socket moves from accepting data to accepting commands if _any_ message is received.
The commands can be send through the OSC server functions and are as follows:
- "/CloseTCPListener", close the socket
- "/SendFileNameToTCP" [_file name here_], send a file name to the socket
- "/Alive", ask the socket to print something to the terminal

The RECORDING command is send when we ask the OSC server to record through the "/RecordStart" handle.
Lastly, the data will be send by the IPhone after the "/Transport" message has been send to it.

### Pipeline Illustrations
![Pipeline](/img/PipelineSignbankProject2.png)

![Pipeline](/img/pipeline.png)

