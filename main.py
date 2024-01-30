from src.config.setup import SetUp
from src.controler import Controller

if __name__ == "__main__":
    args = SetUp("config.yaml")

    key_controller = Controller(args)
    key_controller.start()