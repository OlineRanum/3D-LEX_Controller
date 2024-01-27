import asyncio
import websockets

class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri

    async def connect(self):
        async with websockets.connect(self.uri) as websocket:
            # Send a request for data (if needed)
            # await websocket.send("your request")

            # Wait for a response and receive data
            data = await websocket.recv()
            return data
    

    def retrieve_next_gloss(self):
        raise NotImplementedError

# Usage example
async def main():
    client = WebSocketClient("https://www.gomerotterspeer.nl/Gebarenoverleg/lijst.html")
    data = await client.connect()
    print(data)

# Run the asyncio event loop
asyncio.run(main())

