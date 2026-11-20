from .._imports import *
from .._consts import *
from ..funcs import *



class LandSubsidyViewDialogSetupUiMixin:
    def _setup_ui(self):
        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()
        lbl_year = QLabel("补贴年度：")
        lbl_year.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.cmb_year = QComboBox()
        self.cmb_year.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.cmb_year.addItem("全部")
        filter_layout.addWidget(lbl_year)
        filter_layout.addWidget(self.cmb_year)

        lbl_search = QLabel("搜索姓名：")
        lbl_search.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_search = QLineEdit()
        self.txt_search.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_search.setPlaceholderText("输入姓名搜索...")
        filter_layout.addWidget(lbl_search)
        filter_layout.addWidget(self.txt_search)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.headers = ["序号", "补贴年度", "户主姓名", "身份证号", "电话号码", "银行账号", "金融机构",
                   "发放金额", "上账时间", "耕地面积", "耕地标准", "油菜面积", "油菜标准", "油菜金额"]
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_delete = QPushButton("删除选中")
        btn_delete.setStyleSheet("background-color: #CC0000; color: white; padding: 8px;")
        btn_delete.setEnabled(self.is_admin)
        btn_export = QPushButton("导出Excel")
        btn_export.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; padding: 8px;")
        btn_close = QPushButton("关闭")
        btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px;")
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_export)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        self.cmb_year.currentTextChanged.connect(lambda: self._search_timer.start())
        self.txt_search.textChanged.connect(lambda: self._search_timer.start())
        btn_delete.clicked.connect(self._do_delete)
        btn_export.clicked.connect(self._do_export)
        btn_close.clicked.connect(self.reject)
