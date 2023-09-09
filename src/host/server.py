import asyncio
import websockets
import queue


class WebSocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = None
        self.queue = queue.Queue()

    async def handle_client(self, websocket, path):
        try:
            async for message in websocket:
                # 將 message 放入 queue
                self.queue.put(message)
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket 連線已關閉")

    def start_server(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.server = loop.run_until_complete(
            websockets.serve(self.handle_client, self.host, self.port)
        )
        loop.run_forever()

    def stop_server(self):
        if self.server:
            self.server.close()

    def send_message(self, message):
        self.queue.put(message)

    def get_message(self):
        try:
            message = self.queue.get(block=False)
            return message
        except queue.Empty:
            return None