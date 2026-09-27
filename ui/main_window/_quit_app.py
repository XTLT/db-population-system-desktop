from PyQt6.QtWidgets import QApplication


def _quit_app(self):
    self.tray_icon.hide()
    QApplication.quit()
