from PyQt6.QtWidgets import QSystemTrayIcon
from PyQt6.QtCore import Qt
from core.config import APP_NAME


def closeEvent(self, event):
    event.ignore()
    self.setWindowState(Qt.WindowState.WindowMinimized)
    self.hide()
    self.tray_icon.show()
    self.tray_icon.showMessage(
        APP_NAME,
        "程序已最小化到系统托盘，双击托盘图标可恢复窗口。",
        QSystemTrayIcon.MessageIcon.Information,
        1500
    )
