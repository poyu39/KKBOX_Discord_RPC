# from webbrowser import Chrome
from PyQt5 import QtWidgets, QtGui
from UI import Ui_MainWindow
from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.common.exceptions import WebDriverException
# from msedge.selenium_tools import Edge, EdgeOptions
from selenium.webdriver.chrome.options import Options
from pypresence import Presence

import http.client
import json
import pickle
import time
import threading
import sys
import os

class MainWindow_controller(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_control()

    def setup_control(self):
        global setting
        with open('setting.json') as f:
            setting = json.load(f)

        self.ui.lineEdit_account.setText(setting["ACCOUNT"])
        self.ui.lineEdit_discord_client_id.setText(
            setting["DISCORD_CLIENT_ID"])
        self.ui.lineEdit_driver_name.setText(setting["DRIVER"])

        self.ui.pushButton_open_web_driver.clicked.connect(self.OPEN_WEB_DRIVER)
        self.ui.pushButton_Discord_hook_close.clicked.connect(self.DISCORD_HOOK_CLOSE)
        self.ui.pushButton_Discord_hook_close.setEnabled(False)

    def OPEN_WEB_DRIVER(self):
        global setting
        setting = {
            "ACCOUNT": self.ui.lineEdit_account.text(),
            "DISCORD_CLIENT_ID": self.ui.lineEdit_discord_client_id.text(),
            "DRIVER": self.ui.lineEdit_driver_name.text()
        }
        with open('setting.json', 'w') as f:
            json.dump(setting, f)

        open_web()
        goto_web()
        load_user_data()

        # dc_rpc
        global RPC
        DISCORD_CLIENT_ID = setting['DISCORD_CLIENT_ID']
        RPC = Presence(DISCORD_CLIENT_ID, pipe=0)
        RPC.connect()

        global stop_flag
        stop_flag = False

        self.ui.pushButton_Discord_hook_close.setEnabled(True)

    def DISCORD_HOOK_CLOSE(self):
        global stop_flag
        global driver 
        if stop_flag != True:
            dump_user_data()
            driver.close()
        stop_flag = True
        self.ui.pushButton_Discord_hook_close.setEnabled(False)
        
    def closeEvent(self, event):
        global close_win
        close_win = True
        print('window close')

def open_web():
    global driver
    with open('setting.json') as f:
        setting = json.load(f)
    if setting['DRIVER'] == 'msedgedriver.exe':
        driver = webdriver.Edge('./' + setting['DRIVER'])
    if setting['DRIVER'] == 'chromedriver':
        driver = webdriver.Chrome('./' + setting['DRIVER'])

def goto_web():
    global driver
    driver.get('https://play.kkbox.com/')

def load_user_data():
    global driver
    global setting
    while(driver.current_url != 'data:,'):
        print(driver.current_url)
        break
    
    file_path = './dp_localStorage_temp'
    if os.path.isfile(file_path):
        print('find localStorage')
        driver.delete_all_cookies()
        with open(file_path, 'rb') as f:
            localStorage = pickle.load(f)
        driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", "wp:pref:" + setting['ACCOUNT'] + ":now_playing_ct", localStorage["playtime"])
        driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", "wp:pref:" + setting['ACCOUNT'] + ":audio_quality", localStorage["audio_quality"])
        driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", "wp:pref:" + setting['ACCOUNT'] + ":volume", localStorage["volume"])
        print('load localStorage')
    else:
        print('cant find localStorage !')
    
    file_path = './dp_cookie_temp'
    if os.path.isfile(file_path):
        print('find cookie')
        driver.delete_all_cookies()
        with open(file_path, 'rb') as f:
            cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
        print('load cookie')
    else:
        print('cant find cookie !')

def dump_user_data():
    global driver
    cookies = driver.get_cookies()
    with open('./dp_cookie_temp', 'wb') as f:
        pickle.dump(cookies, f)
    print('dump cookie done')
    
    localStorage = {
        "playtime" : driver.execute_script("return localStorage.getItem('wp:pref:" + setting['ACCOUNT'] + ":now_playing_ct')"),
        "audio_quality" : driver.execute_script("return localStorage.getItem('wp:pref:" + setting['ACCOUNT'] + ":audio_quality')"),
        "volume" : driver.execute_script("return localStorage.getItem('wp:pref:" + setting['ACCOUNT'] + ":volume')")
    }
    with open('./dp_localStorage_temp', 'wb') as f:
        pickle.dump(localStorage, f)
    print('dump localStorage done')

def now_playing():
    global song_data
    global driver
    global stop_flag
    global last_song
    global DISCONNECTED_MSG
    global close_win
    while True:
        if stop_flag == False:
            try:
                song_data["name"] = driver.find_element(By.CLASS_NAME, 'hayDaa').text
                song_data["artist"] = driver.find_element(By.CLASS_NAME, 'yKVKxJ').text
                song_data["image"] = driver.find_element(By.XPATH, '//div[@class="kl3pDr"]//a//img').get_attribute("src")  # kl3pDr
                song_data["playtime"] = driver.find_element(By.XPATH, '//div[@class="bR5Q8S H90HDr"]//span').text  # bR5Q8S H90HDr
                song_data["stop"] = driver.find_element(By.CLASS_NAME, 'q6OLlr').text  # q6OLlr
            except:
                # print('no element')
                pass
            dc_rpc()
        try:
            if driver.get_log('driver')[-1]['message'] == DISCONNECTED_MSG and stop_flag == False:
                print('Browser window closed by user')   
                stop_flag = True
        except:
            pass
        if close_win == True:
            break
        time.sleep(1)

def dc_rpc():
    global RPC
    global setting
    global dc_rpc_act
    global last_playtime
    global start_time
    playtime = song_data["playtime"]
    playtime = int(playtime[0])*600 + int(playtime[1]) * 60 + int(playtime[3])*10 + int(playtime[4])
    stop = abs(min(last_playtime) - max(last_playtime))
    if abs(stop) == 1 or abs(stop) == 2:
        if dc_rpc_act == False:
            start_time = time.time()
            RPC.update(
                state=song_data["artist"],
                details=song_data["name"],
                large_image=song_data["image"],
                large_text='正在聽' + song_data["name"],
                small_image="https://services.garmin.cn/appsLibraryBusinessServices_v0/rest/apps/7d6455f4-6e40-45b2-be8c-e5d4fe089310/icon/e1d1245f-d190-4daf-b16f-7aaea3fdb13c",
                small_text="KKBOX",
                start=start_time - playtime
            )
            print('rpc start at ' + time.ctime(start_time + playtime))
            dc_rpc_act = True
    elif abs(stop) > 3:
        start_time = time.time()
        RPC.update(
            state=song_data["artist"],
            details=song_data["name"],
            large_image=song_data["image"],
            large_text='正在聽' + song_data["name"],
            small_image="https://services.garmin.cn/appsLibraryBusinessServices_v0/rest/apps/7d6455f4-6e40-45b2-be8c-e5d4fe089310/icon/e1d1245f-d190-4daf-b16f-7aaea3fdb13c",
            small_text="KKBOX",
            start=start_time - playtime
            )
        print('rpc update at ' + time.ctime(start_time + playtime))
    elif abs(stop) == 0:
        if dc_rpc_act == True:
            RPC.clear()
            print('rpc clear')
            dc_rpc_act = False
    last_playtime.append(playtime)
    del(last_playtime[0])

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow_controller()
    window.setWindowIcon(QtGui.QIcon("app_icon.ico"))
    window.show()

    # value
    last_playtime = [0, 0, 0]
    stop_flag = True
    last_track = ''
    song_data = {
        "name": "None",
        "artist": "None",
        "image": "None",
        "playtime": "00:00"
    }
    last_song = "None"
    dc_rpc_act = False
    DISCONNECTED_MSG = 'Unable to evaluate script: disconnected: not connected to DevTools\n'
    close_win = False
    
    kkbox = threading.Thread(target=now_playing)
    kkbox.start()
    sys.exit(app.exec_())
