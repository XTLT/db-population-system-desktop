from PyQt6.QtCore import QTimer


def _auto_backup(self):
    timer = QTimer(self)
    timer.timeout.connect(self._do_backup)
    timer.start(24 * 60 * 60 * 1000)
