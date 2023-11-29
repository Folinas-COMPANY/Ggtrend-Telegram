import os
import sys
sys.path.append(os.getcwd())  # NOQA

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from src.core.HomeController import pushNotification

from src.ui import HomeUI


class HomeWindow(QMainWindow):
    def __init__(self):
        super(HomeWindow, self).__init__()
        self.ui = HomeUI.Ui_MainWindow()
        self.ui.setupUi(self)

        # Array for storing mode to run
        self.run_array = []

        self.ui.one_hour_checkbox.clicked.connect(lambda x: self.onCheckModeCrawler(x, 'one_hour'))
        self.ui.one_day_checkbox.clicked.connect(lambda x: self.onCheckModeCrawler(x, 'one_day'))
        self.ui.four_hours_checkbox.clicked.connect(lambda x: self.onCheckModeCrawler(x, 'four_hours'))
        self.ui.seven_days_checkbox.clicked.connect(lambda x: self.onCheckModeCrawler(x, 'seven_days'))
        self.ui.start_button.clicked.connect(self.startButtonEvent)
        self.ui.stop_button.clicked.connect(self.stopButtonEvent)
        self.ui.log_widget.hide()

    def onCheckModeCrawler(self, val, mode):
        print(f"==>> val: {val}")
        print(f"==>> mode: {mode}")

        if val:
            self.run_array.append(mode)
        else:
            self.run_array.remove(mode)

        print(f"==>> run_array: {self.run_array}")

    def startButtonEvent(self):
        print("==>> Start button clicked")
        print(f"==>> run_array: {self.run_array}")

        if len(self.run_array) == 0:
            pushNotification("Please select mode to run !")
            return

    def stopButtonEvent(self):
        print("==>> Stop button clicked")
        print(f"==>> run_array: {self.run_array}")
