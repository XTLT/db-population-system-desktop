"""原模块的 import 头（mixin 共用）。"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.config import FONT_NAME, BTN_SAVE_COLOR, BTN_CANCEL_COLOR
from core.database import authenticate_user
