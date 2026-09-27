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
    ('name', '姓名'),
    ('id_card', '身份证号'),
    ('phone', '电话'),
    ('social_card1', '社保卡1'),
    ('social_card2', '社保卡2'),
    ('social_card3', '社保卡3'),
    ('hu_hao', '户号'),
    ('address', '地址'),
]

MATCH_BY_NAME = 'name'
MATCH_BY_ID_CARD = 'id_card'


class ColumnMappingDialog(QDialog):
    """选择匹配方式和各列填写内容"""

    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.setWindowTitle("列映射设置")
        self.setMinimumSize(600, 480)
        self._headers = headers
        self._field_combos = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        info = QLabel("请设置匹配列和需要填写的数据列：")
        info.setFont(QFont(FONT_NAME, FONT_SIZE))
        layout.addWidget(info)

        match_row = QHBoxLayout()
        match_row.addWidget(QLabel("匹配方式："))
        self.cbo_match = QComboBox()
        self.cbo_match.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.cbo_match.addItem("按姓名匹配", MATCH_BY_NAME)
        self.cbo_match.addItem("按身份证号匹配", MATCH_BY_ID_CARD)
        self.cbo_match.currentDataChanged.connect(self._update_match_combo)
        match_row.addWidget(self.cbo_match)
        match_row.addStretch()
        layout.addLayout(match_row)

        col_row = QHBoxLayout()
        col_row.addWidget(QLabel("匹配列："))
        self.cbo_match_col = QComboBox()
        self.cbo_match_col.setFont(QFont(FONT_NAME, FONT_SIZE))
        for i, h in enumerate(self._headers):
            display = f"第{i+1}列: {h or '(空)'}"
            self.cbo_match_col.addItem(display, i + 1)
        col_row.addWidget(self.cbo_match_col)
        col_row.addStretch()
        layout.addLayout(col_row)

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

    def _update_match_combo(self):
        match_by = self.cbo_match.currentData()
        for combo in self._field_combos:
            for i in range(combo.count()):
                if combo.itemData(i) == match_by:
                    combo.model().item(i).setEnabled(False)
                else:
                    combo.model().item(i).setEnabled(True)

    @property
    def match_by(self):
        return self.cbo_match.currentData()

    @property
    def match_col(self):
        return self.cbo_match_col.currentData()

    @property
    def fill_map(self):
        match_col = self.cbo_match_col.currentData()
        result = {}
        for i, combo in enumerate(self._field_combos):
            val = combo.currentData()
            if val and (i + 1) != match_col:
                result[i + 1] = val
        return result
