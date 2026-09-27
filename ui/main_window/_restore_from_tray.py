from PyQt6.QtCore import Qt


def _restore_from_tray(self):
    self.showNormal()
    self.setWindowState(Qt.WindowState.WindowNoState)
    self.activateWindow()
    self.raise_()
    self.setFocus()
