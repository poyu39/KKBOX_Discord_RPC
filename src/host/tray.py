import os
import PySimpleGUIQt as sg

class Tray:
    def __init__(self):
        self.menu_def = ['BLANK', ['重新連線 Discord', '---', '關閉程式']]  
        self.tray = None

    def create_tray(self):
        self.tray = sg.SystemTray(menu=self.menu_def)

    def read_events(self):
        while True:
            menu_item = self.tray.Read()
            if menu_item == '關閉程式':
                self.close_event()
                break
        
    def close_event(self):
        self.tray.Close()
        os._exit(0)