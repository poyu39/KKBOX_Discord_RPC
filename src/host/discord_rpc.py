from pypresence import Presence


class DiscordRPC:
    def __init__(self, client_id):
        self.client_id = client_id
        self.rpc = None
        self.play_status= 'stop'

    def connect(self):
        self.rpc = Presence(self.client_id, pipe=0)
        self.rpc.connect()
        print('RPC connected')
    
    def update_rpc(self, **kkbox_data):
        self.rpc_data = {
            'state': kkbox_data['song_author'],
            'details': f"{kkbox_data['song_name']} ",
            'large_text': f'正在聽: {kkbox_data["song_name"]}',
            'large_image': kkbox_data['song_image'],
            'small_image': 'https://i.imgur.com/tUEa4Xz.png',
            'small_text': 'KKBOX',
            'buttons': [
                {
                    'label': f'{kkbox_data["song_time"][0]} / {kkbox_data["song_time"][1]}',
                    'url': f"https://play.kkbox.com{kkbox_data['song_url']}"
                }
            ]
        }
        if self.play_status == 'play':
            self.rpc.update(**self.rpc_data)
        elif self.play_status == 'pause':
            self.rpc_data['buttons'][0]['label'] = '暫停中'
            self.rpc.update(**self.rpc_data)
    
    def get_play_status(self):
        return self.play_status
    
    def set_play_status(self, status):
        self.play_status = status
    
    def close(self):
        self.rpc.close()
        print('RPC closed')