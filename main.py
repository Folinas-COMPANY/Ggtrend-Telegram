import os
import sys
import traceback

# sys.path.append(os.getcwd())  # NOQA


from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from src.widget.HomeWindow import HomeWindow
from datetime import datetime
from types import TracebackType


def throw_errors(type, value, tb: TracebackType):
    formatted_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    with open("logs/errorslog.txt", "a") as f:
        f.write(f"==>> Time: {formatted_time}\n")
        f.write(f"==>> Type: {type}\n")
        f.write(f"==>> Value: {value}\n")
        f.write("==>> Traceback:\n")
        traceback.print_tb(tb, file=f)
        f.write("\n")

    print(f"==>> Type: {type}")
    print(f"==>> Value: {value}")
    traceback.print_tb(tb)


if __name__ == '__main__':
    app = QApplication([])

    homeWidget = HomeWindow()

    homeWidget.show()

    sys.excepthook = throw_errors
    sys.exit(app.exec_())
