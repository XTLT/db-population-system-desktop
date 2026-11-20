"""原模块的 import 头（mixin 共用）。"""
import copy
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QHeaderView, QAbstractItemView,
    QLineEdit, QGroupBox, QApplication, QComboBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
from core.config import FONT_NAME, BTN_ADD_COLOR, FONT_SIZE, BTN_CANCEL_COLOR
