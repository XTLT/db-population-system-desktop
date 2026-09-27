from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR


class MultiNameSelectDialog(QDialog):
    """同名多人时弹出，显示每个人详细信息供用户选择"""

    def __init__(self, persons, name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"同名选择 — {name}")
        self.setMinimumSize(750, 350)
        self._persons = persons
        self._selected = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        info = QLabel(f"数据库中找到 {len(self._persons)} 个同名人员，请选择要使用的数据：")
        info.setFont(QFont(FONT_NAME, FONT_SIZE))
        layout.addWidget(info)

        headers = ["姓名", "身份证号", "电话", "户号", "地址", "与户主关系"]
        self.table = QTableWidget()
        self.table.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(self._persons))

        for row, p in enumerate(self._persons):
            values = [
                p.get('name', ''),
                p.get('id_card', ''),
                p.get('phone', ''),
                p.get('hu_hao', ''),
                p.get('address', ''),
                p.get('relation', ''),
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(str(val) if val else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self._confirm)
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_ok = QPushButton("确认选择")
        btn_ok.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 8px 30px;")
        btn_ok.clicked.connect(self._confirm)
        btn_cancel = QPushButton("跳过此人")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px 30px;")
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_ok)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

    def _confirm(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请选择一个人员")
            return
        self._selected = self._persons[row]
        self.accept()

    @property
    def selected_person(self):
        return self._selected
