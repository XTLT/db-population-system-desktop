from .._imports import *
from .._consts import *
from ..funcs import *



class _ColumnSelectDialogMInitMixin:
    def __init__(self, wb, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择补全列")
        self._wb = wb
        layout = QVBoxLayout(self)

        # Sheet 选择
        row_sheet = QHBoxLayout()
        row_sheet.addWidget(QLabel("工作表:"))
        self.cb_sheet = QComboBox(self)
        row_sheet.addWidget(self.cb_sheet, 1)
        layout.addLayout(row_sheet)

        # 姓名列
        row_name = QHBoxLayout()
        row_name.addWidget(QLabel("姓名列:"))
        self.cb_name = QComboBox(self)
        row_name.addWidget(self.cb_name, 1)
        layout.addLayout(row_name)

        # 证件号码列
        row_id = QHBoxLayout()
        row_id.addWidget(QLabel("证件号码列:"))
        self.cb_id = QComboBox(self)
        row_id.addWidget(self.cb_id, 1)
        layout.addLayout(row_id)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        for ws in wb.worksheets:
            self.cb_sheet.addItem(ws.title)
        self.cb_sheet.currentTextChanged.connect(self._load_columns)
        self._load_columns(self.cb_sheet.currentText())
