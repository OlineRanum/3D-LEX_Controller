from src.config.setup import SetUp
# from src.controler import Controller
from src.utils.livelinkface import LiveLinkFaceServer


if __name__ == "__main__":
    args = SetUp("config.yaml")
    # controller = Controller(args)
    server = LiveLinkFaceServer("testGloss", args)
    # Launch Server
    server.init_server()
        

    
    