from PyQt6.QtWidgets import QSystemTrayIcon


def _on_tray_activated(self, reason):
    if reason == QSystemTrayIcon.ActivationReason.Trigger:
        self._restore_from_tray()
