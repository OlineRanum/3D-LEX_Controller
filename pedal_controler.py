from pynput.keyboard import *


def on_press(key):
    print('press ON: {}'.format(key))

def on_release(key):
    print('press OFF: {}'.format(key))
    if key == Key.esc:
        # Stop listener
        return False
# Collect events until released
with Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()

    AAAAaaaaaaa