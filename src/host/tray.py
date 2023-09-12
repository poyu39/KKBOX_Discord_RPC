import os
from PySimpleGUIQt import Text, InputText, Button, Window, SystemTray
from discord_rpc import DiscordRPC
from settings import CONFIG

class Tray:
    def __init__(self):
        self.menu_def = ['BLANK', ['設定 Application ID', '重新連線 Discord', '關閉程式']]
        self.layout = [
            [Text('請輸入 Application ID')],
            [InputText()],
            [Button('確定'), Button('取消')],
        ]
        self.tray = None
        self.window = None
        self.play_status_temp = 'stop'

    def create_tray(self):
        self.tray = SystemTray(menu=self.menu_def, data_base64=CONFIG.ICON, tooltip='KKBOX Discord RPC')
    
    def create_window(self):
        self.window = Window('KKBox Discord RPC', self.layout, finalize=True)

    def read_events(self, rpc: DiscordRPC = None):
        while True:
            menu_item = self.tray.Read()
            if menu_item == '關閉程式':
                self.close_event()
                break
            if menu_item == '重新連線 Discord':
                rpc.reconnect()
            if menu_item == '設定 Application ID':
                if self.window:
                    self.window.Show()
                else:
                    self.create_window()
                # input_text = sg.popup_get_text('請輸入文字：', title='輸入文字', default_text='')
                # if input_text:
                #     sg.popup(f'您輸入的文字是：{input_text}')
            if self.window:
                event, values = self.window.read()
                if event == '確定':
                    self.window.close()
                    with open(f'{CONFIG.WORKDIR}/storage/config.yml', 'w', encoding='utf-8') as f:
                        f.write(f'client_id: {values[0]}')
                    CONFIG.reload()
                    rpc.set_client_id(CONFIG.CLINET_ID)
                    rpc.reconnect()
                elif event == '取消':
                    self.window.close()
    
    def close_event(self):
        self.tray.Close()
        os._exit(0)