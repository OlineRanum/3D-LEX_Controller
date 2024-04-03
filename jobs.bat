REM This batch file starts three separate command prompt windows
REM to run Python scripts concurrently.

start cmd /k python mainController.py
start cmd /k python mainOSC.py
start cmd /k python fileReceiver.py