"""原模块的 import 头（mixin 共用）。"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import json
import os
from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR, APPDATA_DIR
