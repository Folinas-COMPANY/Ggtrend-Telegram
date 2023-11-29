from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


def pushNotification(title):
    msg = QMessageBox()
    msg.setWindowTitle('Thông báo!')
    msg.setTextFormat(Qt.RichText)
    msg.setText(title)
    msg.activateWindow()
    msg.exec_()
    return
