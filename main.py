from src.config.configure_utils import SetUp
from src.hotkey_controler import Controller

if __name__ == "__main__":
    args = SetUp("config/config.yaml")

    key_controller = Controller(args)
    key_controller.start()