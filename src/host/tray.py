import os
import PySimpleGUIQt as sg
from discord_rpc import DiscordRPC
from settings import CONFIG

class Tray:
    def __init__(self):
        self.menu_def = ['BLANK', ['控制狀態: 無', '---', '重新連線 Discord', '關閉程式']]  
        self.tray = None
        self.play_status_temp = 'stop'

    def create_tray(self):
        self.tray = sg.SystemTray(menu=self.menu_def)

    def read_events(self, rpc: DiscordRPC):
        self.rpc = rpc
        while True:
            menu_item = self.tray.Read()
            if menu_item == '關閉程式':
                self.close_event()
                break
            if menu_item == '重新連線 Discord':
                self.reconnect_discord()
    
    def close_event(self):
        self.tray.Close()
        os._exit(0)
        
    def reconnect_discord(self):
        self.rpc.close()
        self.rpc = DiscordRPC(CONFIG.CLINET_ID)
        self.rpc.connect()