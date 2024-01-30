from src.config.setup import SetUp
from src.controler import Controller
from src.utils.livelinkface import LiveLinkFaceServer
from asyncio import run 


if __name__ == "__main__":
    args = SetUp("config.yaml")
    controller = Controller(args)
    server = LiveLinkFaceServer(controller)
    
        

    
    