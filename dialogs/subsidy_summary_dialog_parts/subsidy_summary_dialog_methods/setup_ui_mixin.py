from .._imports import *
from .._consts import *
from ..funcs import *

_HEADERS = None
_LOCAL_MODULES = None
_to_amount = None

class SubsidySummaryDialogSetupUiMixin:
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        title = QLabel(f"{self.person_name}　{self.id_card}")
        title.setFont(QFont(FONT_NAME, 13))
        layout.addWidget(title)

        self.lbl_summary = QLabel("正在加载…")
        self.lbl_summary.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.lbl_summary.setWordWrap(True)
        layout.addWidget(self.lbl_summary)

        self.table = QTableWidget()
        self.table.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table.setColumnCount(len(_HEADERS))
        self.table.setHorizontalHeaderLabels(_HEADERS)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # 银行账号列固定宽度，按最长账号动态计算，避免 19 位号码被挤压截断
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_close = QPushButton("关闭")
        btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px;")
        btn_close.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
