import sys
import os
import ctypes

# Base path resolution for both frozen (PyInstaller) and development
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, BASE_DIR)

# Windows DPI awareness
if sys.platform == 'win32':
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from mainwindow import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Σ Dev Network Monitor")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SigmaDev")
    app.setQuitOnLastWindowClosed(False)  # Keep alive in tray

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
