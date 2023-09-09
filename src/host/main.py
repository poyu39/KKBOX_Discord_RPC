import threading, json, time
from server import WebSocketServer
from discord_rpc import DiscordRPC
from settings import CONFIG
from tray import Tray


def server_thread(websocket_server):
    websocket_server.start_server()
    
def listen_kkbox_data():
    # 從 queue 取出 message
    while True:
        message = server.get_message()
        if message:
            json_message = json.loads(message)
            if json_message['type'] == 'reconnect':
                server.send_message(json.dumps({'type': 'connected'}))
            if json_message['type'] == 'kkbox_data':
                play_status = json_message['data']['play_status']
                kkbox_data = json_message['data']
                if play_status:
                    rpc.set_play_status('play')
                else:
                    rpc.set_play_status('pause')
                rpc.update_rpc(**kkbox_data)
        time.sleep(1)

if __name__ == '__main__':
    server = WebSocketServer('localhost', 9239)
    # 用 thread 啟動 server
    server_thread = threading.Thread(target=server_thread, args=(server,))
    server_thread.start()

    if CONFIG.CLINET_ID:
        rpc = DiscordRPC(CONFIG.CLINET_ID)
        rpc.connect()
    listen_kkbox_data_thread = threading.Thread(target=listen_kkbox_data)
    listen_kkbox_data_thread.start()
    
    tray = Tray()
    tray.create_tray()
    tray.read_events()