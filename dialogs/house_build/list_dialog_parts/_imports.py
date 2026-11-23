"""原模块的 import 头（mixin 共用）。"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QComboBox, QLineEdit, QMessageBox, QFileDialog, QGridLayout,
    QTabWidget, QWidget, QTextEdit, QFormLayout, QGroupBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR
from network.client import (
    api_house_build_list,
    api_house_build_get,
    api_house_build_create,
    api_house_build_update,
    api_house_build_delete,
    api_house_build_prefill,
    api_house_build_download,
    api_house_build_batch_download,
)
