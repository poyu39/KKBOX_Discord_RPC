import subprocess
import time
import logging
import json
import sys
from pathlib import Path

import psutil
import pychrome
from pypresence import Presence


class DiscordRPC:
    def __init__(self, application_id):
        self.rpc = Presence(application_id)
    
    def connect(self):
        try:
            self.rpc.connect()
            return True
        except Exception as e:
            return False
    
    def update(self, **kwargs):
        self.rpc.update(**kwargs)
    
    def clear(self):
        self.rpc.clear()
    
    def close(self):
        self.rpc.close()

class Player:
    def __init__(self, title, artist, image, now_time, status):
        self.title = title
        self.artist = artist
        self.image = image
        self.now_time = now_time
        self.status = status

class KKBOX:
    def __init__(self, kkbox_exe_path, port=9239):
        self.kkbox_exe_path = kkbox_exe_path
        self.port = port
        self.browser = None
        self.tab = None
        self.kkbox_process = None
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def start_kkbox(self):
        self.kkbox_process = subprocess.Popen(
            [self.kkbox_exe_path, f'--remote-debugging-port={self.port}']
        )
        time.sleep(5)
    
    def start_browser(self):
        try:
            self.browser = pychrome.Browser(url=f'http://127.0.0.1:{self.port}')
            self.tab = self.browser.list_tab()[0]
            self.tab.start()
            self.tab.Network.enable()
            self.tab.Page.enable()
        except Exception as e:
            self.logger.error('連接瀏覽器失敗')
            sys.exit(1)
    
    def is_kkbox_running(self):
        if self.kkbox_process.poll() is not None:
            return False
        
        for proc in psutil.process_iter(['pid', 'name']):
            if 'KKBOX' in proc.info['name']:
                return True
        return False
    
    def get_player(self):
        title       = self._get_xpath("//span[@class='_inner_16fkr_30']//a")
        artist      = self._get_xpath("//a[@class='_artist_16fkr_45']")
        image       = self._get_xpath("//div[@class='_cover_16fkr_6']//a//img", 'src')
        now_time    = self._get_xpath("//div[@class='_time-info_czveb_1 _time-info_6q6zi_19']//span[1]")
        play        = self._get_xpath("//button[@class='_button-icon_1h9pm_1 k-icon _opacity-transition_1h9pm_30 k-icon-now_playing-play control']//span[1]")
        pause       = self._get_xpath("//button[@class='_button-icon_1h9pm_1 k-icon _opacity-transition_1h9pm_30 k-icon-now_playing-pause control']//span[1]")
        
        if '' in (title, artist, image, now_time):
            return Player('', '', '', 0, 'paused')
        
        now_time = int(now_time[0]) * 600 + int(now_time[1]) * 60 + int(now_time[3]) * 10 + int(now_time[4])
        
        status = None
        if play != '' and pause == '':
            status = 'paused'
        elif play == '' and pause != '':
            status = 'playing'
        
        return Player(title, artist, image, now_time, status)
    
    def _get_xpath(self, xpath, attr='innerText'):
        xpath_func = f'''
            (function() {{
                let result = document.evaluate("{xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                return result.singleNodeValue ? result.singleNodeValue.{attr} : '';
            }})();
        '''
        return self.tab.Runtime.evaluate(expression=xpath_func)['result']['value']


if __name__ == '__main__':
    storage_path = Path('./storage')
    storage_path.mkdir(exist_ok=True)
    
    config_path = Path(f'{storage_path}/config.json')
    if not config_path.exists():
        with open(config_path, 'w') as f:
            json.dump({
                'kkbox_exe_path': 'C:\\Users\\<user_name>\\AppData\\Local\\Programs\\@universalelectron-shell\\KKBOX.exe',
                'application_id': ''
            }, f, indent=4)
        sys.exit(1)
    
    config = json.load(open(config_path))
    
    kkbox_exe_path = Path(config['kkbox_exe_path'])
    
    app = KKBOX(kkbox_exe_path)
    rpc = DiscordRPC(config['application_id'])
    
    app.start_kkbox()
    app.start_browser()
    
    if rpc.connect():
        app.logger.info('Discord RPC 連接成功')
    else:
        app.logger.error('Discord RPC 連接失敗')
        sys.exit(1)
    
    while True:
        if not app.is_kkbox_running():
            app.logger.error('KKBOX 關閉')
            break
        
        player = app.get_player()
        app.logger.info(f'歌曲: {player.title}, 歌手: {player.artist}, 狀態: {player.status}, 時間: {player.now_time}')
        
        if player.status == 'playing':
            start_time = time.time()
            rpc.update(
                state       = player.artist,
                details     = player.title,
                large_text  = f'正在聽: {player.title}',
                large_image = player.image,
                small_image = 'https://imgur.com/BOIijD9.png',
                small_text  = 'KKBOX Discord RPC',
                start       = start_time - player.now_time
            )
        else:
            rpc.clear()
        
        time.sleep(1)
    
    rpc.clear()
    rpc.close()
