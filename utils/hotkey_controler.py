from pynput import keyboard

class KeyController:
    def __init__(self, args):
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.args = args


    def on_press(self, key):
        try:
            if key.char == self.args.start_key:
                print('{0}: start recording'.format(key.char))
            elif key.char == self.args.stop_key:
                print('{0}: stop recording'.format(key.char))
            elif key.char == self.args.save_key:
                print('{0}: save recording'.format(key.char))
        except AttributeError:
            # Handles special keys that don't have a char attribute
            print('Key not mapped to functionality, please configure in config.yaml')


    def on_release(self, key):
        if key == keyboard.Key.esc:
            # Stop listener
            return False

    def start(self):
        # Start the listener
        with self.listener as listener:
            listener.join()

if __name__ == "__main__":
    recorder = KeyboardRecorder('../config/config.yaml')
    recorder.start()