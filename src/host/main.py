import threading, json, time
from server import WebSocketServer
from discord_rpc import DiscordRPC
from settings import CONFIG


def server_thread(websocket_server):
    websocket_server.start_server()

if __name__ == "__main__":
    server = WebSocketServer("localhost", 9239)
    # 用 thread 啟動 server
    server_thread = threading.Thread(target=server_thread, args=(server,))
    server_thread.start()

    rpc = DiscordRPC(CONFIG.CLINET_ID)
    rpc.connect()
    
    # 從 queue 取出 message
    while True:
        message = server.get_message()
        if message:
            kkbox_data = json.loads(message)
            rpc.update_rpc(**kkbox_data)
        
        time.sleep(1)