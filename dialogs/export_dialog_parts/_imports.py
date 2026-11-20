"""原模块的 import 头（mixin 共用）。"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QFormLayout, QGroupBox, QCheckBox,
    QScrollArea, QWidget, QGridLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from core.config import FONT_NAME, FONT_SIZE
