REM This batch file starts three separate command prompt windows
REM to run Python scripts concurrently.

start cmd /k python3 mainController.py
start cmd /k python3 mainOSC.py
start cmd /k python3 fileReceiver.py