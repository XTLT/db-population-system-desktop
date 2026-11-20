"""原模块的 import 头（mixin 共用）。"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR
from network.client import get_server_url
