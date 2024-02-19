"""
Main script for launching a LiveLinkFaceServer.

This script imports necessary modules to set up and launch a LiveLinkFaceServer instance.
It fetches configuration settings from a YAML file using the SetUp class from src.config.setup module.
Then, it initializes a LiveLinkFaceServer instance with a specified model name and the fetched arguments.
Finally, it launches the server using the init_server() method.

Usage:
    python main.py

    - Ensure 'config.yaml' exists in the 'src.config' directory with required settings.

Modules:
    - SetUp: Class for setting up configurations from a YAML file.
    - LiveLinkFaceServer: Class for handling LiveLinkFace server setup and launch.
"""
from src.config.setup import SetUp
from src.utils.livelinkface import LiveLinkFaceServer


if __name__ == "__main__":
    # Fetch args
    args = SetUp("config.yaml")

    # Setup server client model
    server = LiveLinkFaceServer("testGloss", args)

    # Launch Server
    server.init_server()

