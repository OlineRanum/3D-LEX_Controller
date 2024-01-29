import asyncio
import websockets

class WebSocketClient:
    def __init__(self):

        # Get uri from sys 
        self.uri = ...

    def connect(self):
        raise NotImplementedError

    def retrieve_next_gloss(self):
        raise NotImplementedError

if __name__ == "__main__":
    raise NotImplementedError
