from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox,
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


def _col_letter(n):
    """1 → A, 2 → B, 27 → AA"""
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


class ColumnMappingDialog(QDialog):
    """选择Sheet、表头行、匹配方式和各列填写内容"""

    def __init__(self, wb, parent=None):
        super().__init__(parent)
        self.setWindowTitle("列映射设置")
        self.setMinimumSize(650, 520)
        self._wb = wb
        self._ws = wb.active
        self._headers = []
        self._field_combos = []
        self._setup_ui()
        self._on_sheet_changed()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        info = QLabel("请选择Sheet、表头行、匹配方式和需要填写的数据列：")
        info.setFont(QFont(FONT_NAME, FONT_SIZE))
        layout.addWidget(info)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Sheet："))
        self.cbo_sheet = QComboBox()
        self.cbo_sheet.setFont(QFont(FONT_NAME, FONT_SIZE))
        for name in self._wb.sheetnames:
            self.cbo_sheet.addItem(name)
        self.cbo_sheet.currentIndexChanged.connect(self._on_sheet_changed)
        row1.addWidget(self.cbo_sheet)

        row1.addSpacing(20)
        row1.addWidget(QLabel("表头行："))
        self.spin_header_row = QSpinBox()
        self.spin_header_row.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.spin_header_row.setMinimum(1)
        self.spin_header_row.setValue(1)
        self.spin_header_row.valueChanged.connect(self._on_header_row_changed)
        row1.addWidget(self.spin_header_row)

        row1.addSpacing(20)
        row1.addWidget(QLabel("匹配方式："))
        self.cbo_match = QComboBox()
        self.cbo_match.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.cbo_match.addItem("按姓名匹配", MATCH_BY_NAME)
        self.cbo_match.addItem("按身份证号匹配", MATCH_BY_ID_CARD)
        self.cbo_match.currentIndexChanged.connect(self._update_field_combos)
        row1.addWidget(self.cbo_match)

        row1.addSpacing(20)
        row1.addWidget(QLabel("匹配列："))
        self.cbo_match_col = QComboBox()
        self.cbo_match_col.setFont(QFont(FONT_NAME, FONT_SIZE))
        row1.addWidget(self.cbo_match_col)
        row1.addStretch()
        layout.addLayout(row1)

        table_label = QLabel("各列填写内容：")
        table_label.setFont(QFont(FONT_NAME, FONT_SIZE))
        layout.addWidget(table_label)

        self.table = QTableWidget()
        self.table.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["列号", "表头内容", "填写内容"])
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

    def _on_sheet_changed(self):
        sheet_name = self.cbo_sheet.currentText()
        self._ws = self._wb[sheet_name]
        self.spin_header_row.setMaximum(self._ws.max_row)
        self._on_header_row_changed()

    def _on_header_row_changed(self):
        header_row = self.spin_header_row.value()
        self._headers = []
        max_col = self._ws.max_column
        for col in range(1, max_col + 1):
            val = self._ws.cell(header_row, col).value
            self._headers.append(str(val).strip() if val is not None else "")

        self.cbo_match_col.blockSignals(True)
        self.cbo_match_col.clear()
        for i, h in enumerate(self._headers):
            letter = _col_letter(i + 1)
            display = f"{letter}: {h or '(空)'}"
            self.cbo_match_col.addItem(display, i + 1)
        self.cbo_match_col.blockSignals(False)

        self.table.setRowCount(len(self._headers))
        self._field_combos = []

        for i, h in enumerate(self._headers):
            letter = _col_letter(i + 1)
            idx_item = QTableWidgetItem(letter)
            idx_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, idx_item)

            header_item = QTableWidgetItem(h or "(空)")
            header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 1, header_item)

            combo = QComboBox()
            combo.setFont(QFont(FONT_NAME, FONT_SIZE))
            for val, label in FIELD_OPTIONS:
                combo.addItem(label, val)
            self._field_combos.append(combo)
            self.table.setCellWidget(i, 2, combo)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._update_field_combos()

    def _update_field_combos(self):
        match_by = self.cbo_match.currentData()
        for combo in self._field_combos:
            for i in range(combo.count()):
                combo.model().item(i).setEnabled(combo.itemData(i) != match_by)

    @property
    def ws(self):
        return self._ws

    @property
    def header_row(self):
        return self.spin_header_row.value()

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
