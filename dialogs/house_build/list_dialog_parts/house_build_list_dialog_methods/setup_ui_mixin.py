from .._imports import *
from .._consts import *
from ..funcs import *


class HouseBuildListDialogSetupUiMixin:
    def _setup_ui(self):
        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()
        lbl_search = QLabel("搜索：")
        lbl_search.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_search = QLineEdit()
        self.txt_search.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_search.setPlaceholderText("姓名 / 身份证号 / 户号 / 申请编号 / 电话")
        self.txt_search.setFixedWidth(260)

        lbl_year = QLabel("年度：")
        lbl_year.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_year = QLineEdit()
        self.txt_year.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_year.setPlaceholderText("如 2026")
        self.txt_year.setFixedWidth(80)

        lbl_status = QLabel("状态：")
        lbl_status.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.cmb_status = QComboBox()
        self.cmb_status.setFont(QFont(FONT_NAME, FONT_SIZE))
        for text, value in STATUS_OPTIONS:
            self.cmb_status.addItem(text, value)

        filter_layout.addWidget(lbl_search)
        filter_layout.addWidget(self.txt_search)
        filter_layout.addWidget(lbl_year)
        filter_layout.addWidget(self.txt_year)
        filter_layout.addWidget(lbl_status)
        filter_layout.addWidget(self.cmb_status)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnCount(len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        self.lbl_sum = QLabel("合计：0 条，申请面积合计 0 ㎡")
        self.lbl_sum.setFont(QFont(FONT_NAME, FONT_SIZE))
        layout.addWidget(self.lbl_sum)

        btn_layout = QHBoxLayout()
        btn_new = QPushButton("新建申请")
        btn_new.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; padding: 8px;")
        btn_edit = QPushButton("编辑")
        btn_edit.setStyleSheet("padding: 8px;")
        btn_delete = QPushButton("删除")
        btn_delete.setStyleSheet("background-color: #CC0000; color: white; padding: 8px;")
        btn_xlsx = QPushButton("导出Excel")
        btn_xlsx.setStyleSheet("padding: 8px;")
        btn_pdf = QPushButton("导出PDF")
        btn_pdf.setStyleSheet("padding: 8px;")
        btn_batch_pdf = QPushButton("批量导出PDF")
        btn_batch_pdf.setStyleSheet("padding: 8px;")
        btn_batch_pdf.setToolTip("打开后勾选同一场会议的户，每户 6 页，会议记录和公示多户共用一张")
        btn_refresh = QPushButton("刷新")
        btn_refresh.setStyleSheet("padding: 8px;")
        btn_close = QPushButton("关闭")
        btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px;")

        btn_layout.addWidget(btn_new)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_xlsx)
        btn_layout.addWidget(btn_pdf)
        btn_layout.addWidget(btn_batch_pdf)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        self.txt_search.textChanged.connect(lambda: self._search_timer.start())
        self.txt_year.textChanged.connect(lambda: self._search_timer.start())
        self.cmb_status.currentTextChanged.connect(lambda: self._search_timer.start())
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.cellDoubleClicked.connect(lambda *_: self._do_edit())
        btn_new.clicked.connect(self._do_new)
        btn_edit.clicked.connect(self._do_edit)
        btn_delete.clicked.connect(self._do_delete)
        btn_xlsx.clicked.connect(lambda: self._do_export('xlsx'))
        btn_pdf.clicked.connect(lambda: self._do_export('pdf'))
        btn_batch_pdf.clicked.connect(self._do_batch_export)
        btn_refresh.clicked.connect(self._load_data)
        btn_close.clicked.connect(self.accept)

    def _on_selection_changed(self):
        row = self.table.currentRow()
        if 0 <= row < len(self.items):
            self.current_app_id = self.items[row].get('id')
        else:
            self.current_app_id = None
