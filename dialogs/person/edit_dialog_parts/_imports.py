"""原模块的 import 头（mixin 共用）。"""
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QPushButton, QLabel, QMessageBox, QScrollArea, QWidget,
    QTabWidget, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QPixmap, QFont
from core.config import (
    FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_ADD_COLOR, BTN_CANCEL_COLOR,
    PHOTO_TYPES, GRADES, GRADE_DISPLAY, STUDENT_STATUSES
)
from core.database import (
    update_person, migrate_person,
    get_student_education, save_student_education, delete_student_education,
    get_education_history, get_family_members, Person, StudentEducation
)
from core.utils.validators import validate_id_card, validate_phone, install_digit_filter
from data.photo_manager import save_photo, delete_photo, get_photo_path, get_photo_status
from network.client import get_server_url
from dialogs.person.relation_list import RELATIONS
