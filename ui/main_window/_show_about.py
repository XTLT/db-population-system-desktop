from PyQt6.QtWidgets import QMessageBox
from core.config import APP_NAME


def _show_about(self):
    from core.config import APP_VERSION
    QMessageBox.about(
        self, "关于",
        f"{APP_NAME}\n版本：{APP_VERSION}\n\n基于Python + PyQt6 + SQLite"
    )
