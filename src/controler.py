from pynput import keyboard
from Client.vicon_client import ViconController
from clients.websocket_client import WebSocketClient
from src.utils.filemanager import FileManager

class Controller:
    def __init__(self, args):
        self.listener = keyboard.Listener(
            on_press=self.__on_press,
            on_release=self.__on_release
        )
        self.args = args
        file_manager = FileManager()
        
        self.vc = ViconController()
        # Set the filename to the first gloss
        self.vc.set_filename(self.gloss)
    
        self.wsc  = WebSocketClient()


        # Issue request to ws to display next gloss
        self.gloss = self.wsc.retrieve_next_gloss()
        

    def __on_press(self, key):
        try:
            if key.char == self.args.start_key:
                print('{0}: start recording'.format(key.char))
                #emit signal to vicon client to start recording
                self.vc.start_capture()

            elif key.char == self.args.stop_key:
                print('{0}: stop recording'.format(key.char))
                # emit signal to vicon client to stop recording
                self.vc.stop_capture()

            elif key.char == self.args.save_key:
                print('{0}: save recording'.format(key.char))
                self.vc.save_capture(self.gloss)
                # Request next gloss from 
                self.wsc.request_next_gloss()
                # Set the filename to the next gloss
                self.vc.set_filename(self.gloss)

        except AttributeError:
            # Handles special keys that don't have a char attribute
            print('Key not mapped to functionality, please configure in config.yaml')


    def __on_release(self, key):
        if key == keyboard.Key.esc:
            # Stop listener
            return False


    def request_next_gloss(self):
        self.file_manager.save_gloss(self.gloss)
        self.gloss = self.wsc.retrieve_next_gloss()
        print("Saving recording...")



    def start(self):
        # Start the listener
        with self.listener as listener:
            listener.join()



if __name__ == "__main__":
    recorder = Controller('../config/config.yaml')
    recorder.start()