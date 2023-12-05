import json
import os
import random
import pause
import sys
sys.path.append(os.getcwd())  # NOQA

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from src.core.HomeController import GetInfomationThread, pushNotification, pushYNQuestion
import datetime
from src.ui import ui_home


class HomeWindow(QMainWindow):
    def __init__(self):
        super(HomeWindow, self).__init__()
        self.ui = ui_home.Ui_MainWindow()
        self.ui.setupUi(self)

        # Array for storing mode to run
        self.run_array = []
        self.crawlerThreads = []
        self.ui.one_hour_checkbox.clicked.connect(lambda x: self.onCheckModeCrawler(x, '1_hour'))
        self.ui.one_day_checkbox.clicked.connect(lambda x: self.onCheckModeCrawler(x, '1_day'))
        self.ui.four_hours_checkbox.clicked.connect(lambda x: self.onCheckModeCrawler(x, '4_hours'))
        self.ui.seven_days_checkbox.clicked.connect(lambda x: self.onCheckModeCrawler(x, '7_days'))
        self.ui.start_button.clicked.connect(lambda: self.startButtonEvent())
        self.ui.stop_button.clicked.connect(self.stopButtonEvent)
        # self.ui.autoRun.clicked.connect(self.autoRunUpdate)
        self.telegramJson = self.getTelegramJson()
        self.keyword = ['shirt', 'sweatshirt', 't shirt', 'hoodie', 'coffee mug',
                        'poster', 'sticker', 'hat', 'sweater', 'blanket', 'mug']

    def getTelegramJson(self):
        with open('./config/telegram_chat_ids.json', 'r+', encoding="utf-8") as f:
            json_data = json.load(f)
            return json_data

    def autoRunUpdate(self, auto):
        thisWindow = self

        class runInBg(QThread):
            def __init__(self):
                super().__init__()
                self.isForcedStop = False

            def run(self):
                if not auto:
                    thisWindow.startRunning()
                    return

                thisWindow.startRunning()

                while not self.isForcedStop:
                    now = datetime.datetime.now()
                    future = now + datetime.timedelta(minutes=thisWindow.ui.timeValue.value())

                    year = future.year
                    month = future.month
                    day = future.day
                    hour = future.hour
                    minute = future.minute

                    pause.until(
                        datetime.datetime(year, month, day, hour, minute, 0)
                    )

                    thisWindow.startRunning()

        self.autoRunThread = runInBg()
        self.autoRunThread.start()

    def onCheckModeCrawler(self, val, mode):

        if val:
            self.run_array.append(mode)
        else:
            self.run_array.remove(mode)

        print(f"==>> run_array: {self.run_array}")

    def startButtonEvent(self, notification=True):
        print(f"==>> notification: {notification}")
        if len(self.run_array) == 0:
            pushNotification("Please select mode to run !")
            return
        if notification:
            print('có')
            res = pushYNQuestion('Bạn có muốn bắt đầu không?')
            if not res:
                return

        self.autoRunUpdate(self.ui.autoRun.isChecked())

    def startRunning(self):
        for mode in self.run_array:
            keywords = self.telegramJson[mode]

            thread = GetInfomationThread(mode, keywords)
            thread.error_signal.connect(pushNotification)
            self.crawlerThreads.append(thread)
            thread.start()

    def stopButtonEvent(self):
        try:
            self.autoRunThread.isForcedStop = True
            self.autoRunThread.terminate()
        except:
            pass
        for thread in self.crawlerThreads:
            thread: GetInfomationThread
            thread.forceStop()
        pushNotification('Đã dừng tất cả!!!')
