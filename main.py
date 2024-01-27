from config.configure_utils import SetUp
from utils.hotkey_controler import KeyController

if __name__ == "__main__":
    args = SetUp("config/config.yaml")
    key_controller = KeyController(args)
    key_controller.start()