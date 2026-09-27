import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon
from core.config import APP_NAME
from network.client import get_server_url


def __init__(self, current_user=None):
    QMainWindow.__init__(self)
    self.current_user = current_user or {}
    self.is_network_mode = bool(get_server_url())
    mode_text = "【网络模式】" if self.is_network_mode else "【本地模式】"
    self.setWindowTitle(f"{APP_NAME} {mode_text}")
    icon_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if getattr(sys, 'frozen', False):
        icon_dir = os.path.dirname(sys.executable)
    window_icon = os.path.join(icon_dir, "window_icon.png")
    if os.path.exists(window_icon):
        self.setWindowIcon(QIcon(window_icon))
    else:
        ico = os.path.join(icon_dir, "app.ico")
        if os.path.exists(ico):
            self.setWindowIcon(QIcon(ico))
    screen = QApplication.primaryScreen().geometry()
    w = min(1400, int(screen.width() * 0.85))
    h = min(900, int(screen.height() * 0.85))
    self.resize(w, h)
    self.matches = []
    self.current_name = None
    self.current_family = []
    self.current_hu_hao = None
    self._update_dialog = None
    self._setup_ui()
    self._setup_menu()
    self._setup_tray()
    if not self.is_network_mode:
        self._auto_backup()
        self._check_grade_promotion()
