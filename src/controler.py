from pynput import keyboard
from asyncio import run
#from src.utils.vicon import ShogunClient
#from src.utils.websocket_client import WebSocketClient
from src.utils.filemanager import FileManager
from src.utils.livelinkface import LiveLinkFaceClient, LiveLinkFaceServer


class Controller:
    def __init__(self, args):

        self.listener = keyboard.Listener(
            on_press=self.__on_press,
            on_release=self.__on_release
        )

        self.args = args

        # For managing and cleaning up files
        self.file_manager = FileManager(self.args.output_dir)

        # TODO: Set up websocket client for Gomer
        # Interactions with Gebarenoverleg platform
        #self.wsc  = WebSocketClient()

        # Initialize first sign
        # Issue request to ws to display first gloss
        #self.gloss = self.wsc.retrieve_next_gloss()
        # TODO: build directory

        # TODO: Remove
        # For testing 
        self.gloss = "testgloss"
        self.file_manager.create_directory(self.args.output_dir + '/' + self.gloss, subdir = True)

        # Interactions with Vicon Shogun
        #self.vc = ShogunClient(self.args, self.gloss)

        # Interactions with HandEngine
        # Currently controlled through integrations in shogun live

        # Interactions with Live Link Face / iPhone AR Kit
        self.llfc = LiveLinkFaceClient(self.args, self.gloss) 
        
        
        # File Counter  
        # We do it like this to not have to search through all files in a directory 
        # after many recordings
        self.file_counter = 0



    def __on_press(self, key):
        try:
            #--------------------------------------------
            # Start recording when start key is pressed
            #--------------------------------------------
            if key.char == self.args.start_key:
                # Remove old version if it exists
                if self.file_counter == 1:
                    # TODO: build function to clean directory
                    self.file_manager.clean_dir(self.args.output_dir + '/' + self.gloss)
                
                print('{0}: start recording'.format(key.char))
                # Trigger vicon to start recording
                #self.vc.start_capture()
                # Hand engine automatically triggered if trigger congifured in shogun live

                # Trigger LLF to start recording
                self.takenumber = self.llfc.start_capture()

                self.file_counter = 1

            #--------------------------------------------
            # Stop recording when stop key is pressed
            #--------------------------------------------
            elif key.char == self.args.stop_key:
                print('{0}: stop recording'.format(key.char))
                # Trigger vicon to stop recording
                # Hand engine automatically triggered if trigger congifured in shogun live
                #self.vc.stop_capture()

                # Trigger LLF to stop recording
                self.llfc.stop_capture()
                
            #--------------------------------------------
            # Save recording when save key is pressed
            #--------------------------------------------
            elif key.char == self.args.save_key:
                print('{0}: save recording'.format(key.char))
                self.llfc.request_battery()
                # Save recording in vicon
                #self.vc.save_capture(self.gloss)
                
                # Export recording from LLF to computer 
                

                # collect an pickle data
                #self.file_manager.export_pickle(self.gloss)

                # Request next gloss from Gebarenoverleg platform
                #self.gloss = self.wsc.request_next_gloss()

                # TODO: build directory
                #self.file_manager.create_directory(self.args.output_dir + '/' + self.gloss)
                
                #self.llfc.save_file()
                # Set the filename to the next gloss
                #self.vc.set_filename(self.gloss)
                #self.llfc.set_filename(self.gloss)
                

                # reset file_counter
                self.file_counter = 0
            else: 
                print('Key not mapped to functionality, please configure in config.yaml')

        except AttributeError as e:
            # Handles special keys that don't have a char attribute
            print(f"AttributeError: {e}")


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



