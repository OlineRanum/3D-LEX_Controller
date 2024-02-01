# data_acquisition

_Instructions in development..._

### Setting up environment
Install requirements
    pip install -r setup/requirements.txt


### Current Pipeline

![Pipeline](/img/pipeline.png)


### Current todos 
[9:36 AM] Oline Ranum
- Decide on the output file format for mocap 
- Fix server for automatically loading files from iphone 
- Make code to collect files from all systems and pickle them
- Make a batching system to feed files from Shogun Live into Post 

# handles / functions for the OSC server
In order to communicate with the OSC server, we use handles. The following handles are defined:
- "/QuitServer", quits the server and closes the python script
- "/SetFileName", takes a _gloss_ and sets the filename to the gloss name
- "/RecordStart", requests the IPhone to start capturing
-  "/RecordStop", requests the IPhone to stop capturing (IPhone should respond with "/RecordStopConfirm", which triggers saving algorithm)
- "/BatteryQuery", requests the battery value of the IPhone and outputs it to the terminal
- "/*", everything else will be printed in the terminal

