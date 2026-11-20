"""原模块的 import 头（mixin 共用）。"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QPushButton, QLabel, QMessageBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR
from core.database import add_person
from core.utils import calculate_age
from core.utils.validators import validate_id_card, validate_phone, install_digit_filter
from core.database import Person
from network.client import get_server_url
from dialogs.person.relation_list import RELATIONS
