from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR

FIELD_OPTIONS = [
    ('', '不填写'),
    ('id_card', '身份证号'),
    ('phone', '电话'),
    ('social_card1', '社保卡1'),
    ('social_card2', '社保卡2'),
    ('social_card3', '社保卡3'),
    ('hu_hao', '户号'),
    ('address', '地址'),
]


class ColumnMappingDialog(QDialog):
    """选择姓名匹配列和各列填写内容"""

    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.setWindowTitle("列映射设置")
        self.setMinimumSize(600, 450)
        self._headers = headers
        self._field_combos = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        info = QLabel("请设置姓名匹配列和需要填写的数据列：")
        info.setFont(QFont(FONT_NAME, FONT_SIZE))
        layout.addWidget(info)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("姓名匹配列："))
        self.cbo_name = QComboBox()
        self.cbo_name.setFont(QFont(FONT_NAME, FONT_SIZE))
        for i, h in enumerate(self._headers):
            display = f"第{i+1}列: {h or '(空)'}"
            self.cbo_name.addItem(display, i + 1)
        name_row.addWidget(self.cbo_name)
        name_row.addStretch()
        layout.addLayout(name_row)

        table_label = QLabel("各列填写内容：")
        table_label.setFont(QFont(FONT_NAME, FONT_SIZE))
        layout.addWidget(table_label)

        self.table = QTableWidget()
        self.table.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["列序号", "列标题", "填写内容"])
        self.table.setRowCount(len(self._headers))

        for i, h in enumerate(self._headers):
            idx_item = QTableWidgetItem(f"第{i+1}列")
            idx_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, idx_item)

            header_item = QTableWidgetItem(str(h or "(空)"))
            header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 1, header_item)

            combo = QComboBox()
            combo.setFont(QFont(FONT_NAME, FONT_SIZE))
            for val, label in FIELD_OPTIONS:
                combo.addItem(label, val)
            self._field_combos.append(combo)
            self.table.setCellWidget(i, 2, combo)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_ok = QPushButton("确定")
        btn_ok.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 8px 30px;")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px 30px;")
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_ok)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

    @property
    def name_col(self):
        return self.cbo_name.currentData()

    @property
    def fill_map(self):
        name_col = self.cbo_name.currentData()
        result = {}
        for i, combo in enumerate(self._field_combos):
            val = combo.currentData()
            if val and (i + 1) != name_col:
                result[i + 1] = val
        return result
