"""原模块的 import 头（mixin 共用）。"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QProgressBar, QFileDialog, QLineEdit, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime
from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR
from ..._import_precheck import confirm_precheck
