from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pypresence import Presence
import json
import time
import os
import sys


class KKBOX_Discord_RPC:
    def __init__(self, url):
        chrome_options = Options()
        chrome_options.add_argument(f'--app={url}')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.driver = webdriver.Chrome(options=chrome_options)
        self.is_save_cookies = False
        
        # create appdata folder
        self.appdata_path = os.path.join(os.getenv('APPDATA'), 'KKBOX_Discord_RPC')
        if not os.path.isdir(self.appdata_path):
            os.mkdir(self.appdata_path)
        
        self.config_path = os.path.join(self.appdata_path, 'config.json')
        if not os.path.isfile(self.config_path):
            with open(self.config_path, 'w') as file:
                json.dump({'application_id': ''}, file)
        
        self.cookies_path = os.path.join(self.appdata_path, 'cookies.json')
        if not os.path.isfile(self.cookies_path):
            with open(self.cookies_path, 'w') as file:
                json.dump([], file)
        
        self.local_storage_path = os.path.join(self.appdata_path, 'local_storage.json')
        if not os.path.isfile(self.local_storage_path):
            with open(self.local_storage_path, 'w') as file:
                json.dump({}, file)
        
        self.local_storage = {}
        self.song_data = {
            'name': '',
            'artist': '',
            'image': '',
            'now_time': 0,
            'end_time': 0,
            'status': ''
        }
        self.last_time = 0
        self.rpc_activity = False

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
    
    def load_cookies(self):
        with open(self.cookies_path, 'r') as file:
            cookies = json.load(file)
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        print('cookies loaded')
    
    def save_cookies(self):
        cookies = self.driver.get_cookies()
        with open(self.cookies_path, 'w') as file:
            json.dump(cookies, file)
        print('cookies saved')
        self.is_save_cookies = True
    
    def load_local_storage(self):
        if os.path.isfile(self.local_storage_path):
            with open(self.local_storage_path, 'r') as file:
                local_storage = json.load(file)
                for key in local_storage:
                    self.driver.execute_script(
                        f'window.localStorage.setItem(arguments[0], arguments[1]);',
                        f'{key}',
                        f'{local_storage[key]}'
                    )
            print('local_storage loaded')
    
    def dump_local_storage(self):
        local_storage_raw = app.driver.execute_script('return window.localStorage;')
        for key in local_storage_raw:
            self.local_storage[key] = local_storage_raw[key]

    def save_local_storage(self):
        with open(self.local_storage_path, 'w') as file:
            json.dump(self.local_storage, file)
        print('local_storage saved')
    
    def check_browser_active(self):
        try:
            self.driver.title
            return True
        except Exception as e:
            return False
    
    def get_song_data(self):
        try:
            self.song_data['name'] = self.driver.find_element(By.XPATH, "//span[@class='_inner_16fkr_30']//a").text
            self.song_data['artist'] = self.driver.find_element(By.XPATH, "//a[@class='_artist_16fkr_45']").text
            self.song_data['image'] = self.driver.find_element(By.XPATH, "//div[@class='_cover_16fkr_6']//a//img").get_attribute('src')
            self.song_data['now_time'] = self.driver.find_element(By.XPATH, "//div[@class='_time-info_czveb_1 _time-info_6q6zi_19']//span[1]").text
            # convert time to second
            self.song_data['now_time'] = int(self.song_data['now_time'][0])*600 + int(self.song_data['now_time'][1])*60 + int(self.song_data['now_time'][3])*10 + int(self.song_data['now_time'][4])
        except Exception as e:
            pass
        if self.song_data['now_time']:
            if self.last_time < self.song_data['now_time']:
                self.song_data['status'] = 'playing'
            else:
                self.song_data['status'] = 'paused'
            self.last_time = self.song_data['now_time']

    def connect_discord_rpc(self):
        with open(self.config_path, 'r') as file:
            application_id = json.load(file)['application_id']
        if application_id == '':
            application_id = self.input_application_id()
        try:
            self.RPC = Presence(application_id)
            self.RPC.connect()
        except Exception as e:
            print('connect discord rpc failed')
            prompt_script = '''
                alert("連接 Discord RPC 失敗，請輸入 Application ID。");
            '''
            self.driver.execute_script(prompt_script)
            while EC.alert_is_present()(self.driver):
                pass
            with open(self.config_path, 'r') as file:
                application_id = ''
            self.driver.quit()
    
    def input_application_id(self):
        prompt_script = 'window.application_id = prompt("請輸入 Application ID");'
        self.driver.execute_script(prompt_script)
        while EC.alert_is_present()(self.driver):
            pass
        application_id = self.driver.execute_script('return window.application_id;')
        print(application_id)
        with open(self.config_path, 'w') as file:
            json.dump({'application_id': application_id}, file)
        return application_id

    def dc_rpc(self):
        if self.RPC is None:
            return
        if self.song_data['status'] == 'playing' and not self.rpc_activity:
            start_time = time.time()
            playtime = self.song_data['now_time']
            self.rpc_data = {
                'state': self.song_data['artist'],
                'details': f"{self.song_data['name']} ",
                'large_text': f"正在聽: {self.song_data['name']}",
                'large_image': self.song_data['image'],
                'small_image': 'https://i.imgur.com/BOIijD9.png',
                'small_text': 'KKBOX Discord RPC',
                'start': start_time - playtime
            }
            self.RPC.update(**self.rpc_data)
            self.rpc_activity = True
        elif self.song_data['status'] == 'paused' and self.rpc_activity:
            self.RPC.clear()
            self.rpc_activity = False


if __name__ == '__main__':
    app = KKBOX_Discord_RPC('https://play.kkbox.com')
    app.load_cookies()
    app.load_local_storage()
    app.connect_discord_rpc()
    while app.check_browser_active():
        if not app.is_save_cookies:
            if app.driver.current_url == 'https://play.kkbox.com/discover/featured':
                app.save_cookies()
                app.is_save_cookies = True
        app.dump_local_storage()
        app.get_song_data()
        app.dc_rpc()
        time.sleep(1)
    app.save_local_storage()
    try:
        app.RPC.close()
        app.driver.quit()
    except:
        pass