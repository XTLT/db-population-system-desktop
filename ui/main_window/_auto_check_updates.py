from PyQt6.QtCore import QTimer
from .workers import VersionCheckWorker


def _auto_check_updates(self):
    """启动后自动检查更新（有更新才弹窗，无更新/失败静默不打扰）。"""
    if getattr(self, '_auto_check_running', False):
        return
    self._auto_check_running = True

    def _on_done(result, error):
        self._auto_check_running = False
        if result and not error:
            QTimer.singleShot(500, lambda: self._show_update_dialog(result))
        # 无更新或检查失败：静默

    self._auto_worker = VersionCheckWorker()
    self._auto_worker.finished.connect(_on_done)
    self._auto_worker.start()
