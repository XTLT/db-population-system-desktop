import sys
import os
from PyQt6.QtWidgets import QMenu, QSystemTrayIcon
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPixmap, QIcon, QPainter, QFont
from core.config import APP_NAME


def _setup_tray(self):
    icon_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if getattr(sys, 'frozen', False):
        icon_dir = os.path.dirname(sys.executable)
    tray_icon_path = os.path.join(icon_dir, "tray_icon.png")
    if os.path.exists(tray_icon_path):
        self._tray_icon_obj = QIcon(tray_icon_path)
    else:
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(0, 102, 204))
        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "人")
        painter.end()
        self._tray_pixmap = pixmap
        self._tray_icon_obj = QIcon(pixmap)

    self.tray_icon = QSystemTrayIcon(self._tray_icon_obj)
    self.tray_icon.setToolTip(APP_NAME)
    tray_menu = QMenu()
    show_action = tray_menu.addAction("显示窗口")
    show_action.triggered.connect(self._restore_from_tray)
    tray_menu.addSeparator()
    quit_action = tray_menu.addAction("退出")
    quit_action.triggered.connect(self._quit_app)
    self.tray_icon.setContextMenu(tray_menu)
    self.tray_icon.activated.connect(self._on_tray_activated)
    if not self.tray_icon.show():
        pass
