from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QPushButton, QLabel, QDateEdit
)
from PyQt6.QtCore import Qt, QDate

from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR
MIGRATION_REASONS = [
    "婚嫁迁出",
    "工作调动",
    "升学迁出",
    "投靠亲属",
    "购房迁入",
    "其他"
]
class MigrationDialog(QDialog):
    def __init__(self, person_name: str, parent=None):
        super().__init__(parent)
        self.person_name = person_name
        self.setWindowTitle("户籍迁出")
        self.setFixedSize(400, 280)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        from PyQt6.QtGui import QFont
        font = QFont(FONT_NAME, FONT_SIZE)

        title = QLabel(f"将人员 {self.person_name} 标记为户籍迁出")
        title.setFont(QFont(FONT_NAME, 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setFont(font)

        self.txt_place = QLineEdit()
        self.txt_place.setFont(font)
        self.txt_place.setPlaceholderText("可选")

        self.cbo_reason = QComboBox()
        self.cbo_reason.setFont(font)
        self.cbo_reason.addItems(MIGRATION_REASONS)
        self.cbo_reason.setEditable(True)
        self.cbo_reason.setCurrentText("")

        form.addRow(QLabel("迁出时间："), self.date_edit)
        form.addRow(QLabel("迁出地："), self.txt_place)
        form.addRow(QLabel("迁出原因："), self.cbo_reason)
        layout.addLayout(form)

        save_layout = QHBoxLayout()
        btn_save = QPushButton("保存")
        btn_save.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 10px;")
        btn_save.clicked.connect(self._save)
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 10px;")
        btn_cancel.clicked.connect(self.reject)
        save_layout.addWidget(btn_save)
        save_layout.addWidget(btn_cancel)
        layout.addLayout(save_layout)

    def get_data(self) -> dict:
        return {
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "place": self.txt_place.text().strip(),
            "reason": self.cbo_reason.currentText().strip()
        }

    def _save(self):
        self.accept()
