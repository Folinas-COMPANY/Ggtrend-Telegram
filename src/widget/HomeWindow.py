import os
import random
import sys
sys.path.append(os.getcwd())  # NOQA

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from src.core.HomeController import GetInfomationThread, pushNotification

from src.ui import HomeUI


class HomeWindow(QMainWindow):
    def __init__(self):
        super(HomeWindow, self).__init__()
        self.ui = HomeUI.Ui_MainWindow()
        self.ui.setupUi(self)

        # Array for storing mode to run
        self.run_array = []
        self.crawlerThreads = []
        self.ui.one_hour_checkbox.clicked.connect(lambda x: self.onCheckModeCrawler(x, 'one_hour'))
        self.ui.one_day_checkbox.clicked.connect(lambda x: self.onCheckModeCrawler(x, 'one_day'))
        self.ui.four_hours_checkbox.clicked.connect(lambda x: self.onCheckModeCrawler(x, 'four_hours'))
        self.ui.seven_days_checkbox.clicked.connect(lambda x: self.onCheckModeCrawler(x, 'seven_days'))
        self.ui.start_button.clicked.connect(self.startButtonEvent)
        self.ui.stop_button.clicked.connect(self.stopButtonEvent)
        self.ui.log_widget.hide()
        
        self.keyword = ['shirt','sweatshirt','t shirt','hoodie','coffee mug','poster','sticker','hat','sweater','blanket','mug']

    def onCheckModeCrawler(self, val, mode):
     

        if val:
            self.run_array.append(mode)
        else:
            self.run_array.remove(mode)

        print(f"==>> run_array: {self.run_array}")

    def startButtonEvent(self):
        if len(self.run_array) == 0:
            pushNotification("Please select mode to run !")
            return
        
        for mode in self.run_array:
            thread = GetInfomationThread(mode,random.choice(self.keyword))
            thread.error_signal.connect(pushNotification)
            self.crawlerThreads.append(thread)
            thread.start()

    def stopButtonEvent(self):
        for thread in self.crawlerThreads:
            thread: GetInfomationThread
            thread.forceStop()
        pushNotification('Đã dừng tất cả!!!')            
