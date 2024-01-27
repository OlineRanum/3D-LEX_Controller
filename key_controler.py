from pynput import keyboard

class KeyboardRecorder:
    def __init__(self):
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )

    def on_press(self, key):
        try:
            if key.char == 'r':
                print('{0}: start recording'.format(key.char))
            elif key.char == 'e':
                print('{0}: stop recording'.format(key.char))
            elif key.char == 's':
                print('{0}: save recording'.format(key.char))
            else:
                print('Please select r for start recording, e for stop recording, s for save recording')
        except AttributeError:
            # Handles special keys that don't have a char attribute
            print('Special key {0} pressed'.format(key))

    def on_release(self, key):
        print('{0} released'.format(key))
        if key == keyboard.Key.esc:
            # Stop listener
            return False

    def start(self):
        # Start the listener
        with self.listener as listener:
            listener.join()

if __name__ == "__main__":
    recorder = KeyboardRecorder()
    recorder.start()