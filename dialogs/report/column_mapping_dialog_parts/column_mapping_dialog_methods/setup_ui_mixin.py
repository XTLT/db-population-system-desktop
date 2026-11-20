from .._imports import *
from .._consts import *
from ..funcs import *

FIELD_OPTIONS = None
MATCH_BY_ID_CARD = None
MATCH_BY_NAME = None
_col_letter = None

class ColumnMappingDialogSetupUiMixin:
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
