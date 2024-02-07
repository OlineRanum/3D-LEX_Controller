from src.config.setup import SetUp
from src.utils.livelinkface import LiveLinkFaceServer


if __name__ == "__main__":
    # Fetch args
    args = SetUp("config.yaml")

    # Setup server client model
    server = LiveLinkFaceServer("testGloss", args)

    # Launch Server
    server.init_server()

