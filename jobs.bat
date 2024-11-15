REM This batch file starts three separate command prompt windows
REM to run Python scripts concurrently.

start cmd /k "title Main Controller & python mainController.py"
start cmd /k "title Main OSC & python mainOSC.py"
start cmd /k "title File Receiver & python fileReceiver.py"
start cmd /k "title Leffe Con & python leffeCon.py"