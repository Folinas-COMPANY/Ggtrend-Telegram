import typing
from abc import abstractmethod
from PyQt5.QtCore import QObject
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class BaseWorker(QObject):
    def __init__(self, parent: QObject | None = ...) -> None:
        super(BaseWorker, self).__init__(parent)

        self.started = pyqtSignal()
        self.finished = pyqtSignal()
        self.is_running = False

    @abstractmethod
    def run(self):
        pass
