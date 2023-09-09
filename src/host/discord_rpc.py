import time
from pypresence import Presence


class DiscordRPC:
    def __init__(self, client_id):
        self.client_id = client_id
        self.rpc = None

    def connect(self):
        self.rpc = Presence(self.client_id, pipe=0)
        self.rpc.connect()
        print('RPC connected')
    
    def update_rpc(self, **kkbox_data):
        self.rpc.update(
            state=kkbox_data['song_author'],
            details=f"{kkbox_data['song_name']} ",
            large_text= f'正在聽: {kkbox_data["song_name"]}',
            large_image=kkbox_data['song_image'],
            small_image='https://i.imgur.com/tUEa4Xz.png',
            small_text='KKBOX',
            buttons=[
                {
                    'label': f'{kkbox_data["song_time"][0]} / {kkbox_data["song_time"][1]}',
                    'url': f"https://play.kkbox.com{kkbox_data['song_url']}"
                }
            ]
        )
        print('RPC updated')