from .._imports import *
from .._consts import *
from ..funcs import *



class DibaoViewDialogSetupUiMixin:
    def _setup_ui(self):
        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()
        lbl_period = QLabel("费款所属期：")
        lbl_period.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_period = QLineEdit()
        self.txt_period.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_period.setPlaceholderText("如：202606")
        self.txt_period.setMaximumWidth(120)

        lbl_id_card = QLabel("身份证号：")
        lbl_id_card.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_id_card = QLineEdit()
        self.txt_id_card.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_id_card.setPlaceholderText("身份证号搜索")
        self.txt_id_card.setMaximumWidth(180)

        btn_search = QPushButton("查询")
        btn_search.setFont(QFont(FONT_NAME, FONT_SIZE))
        btn_search.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; padding: 6px 16px;")
        btn_search.clicked.connect(self._load_data)

        self.lbl_count = QLabel("")
        self.lbl_count.setFont(QFont(FONT_NAME, FONT_SIZE))

        filter_layout.addWidget(lbl_period)
        filter_layout.addWidget(self.txt_period)
        filter_layout.addWidget(lbl_id_card)
        filter_layout.addWidget(self.txt_id_card)
        filter_layout.addWidget(btn_search)
        filter_layout.addWidget(self.lbl_count)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.headers = ["费款所属期", "姓名", "身份证号", "村名称", "性别", "和申请人关系",
                   "共同生活家庭成员", "享受保障人口数", "家庭保障总金额", "家庭最低生活基本保障金",
                   "家庭特殊困难补助金", "家庭调剂金额", "特殊困难情形", "特殊困难补助金",
                   "初始享受时间", "始发年月", "导入来源", "银行账号"]
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

        btn_delete.clicked.connect(self._do_delete)
        btn_export.clicked.connect(self._do_export)
        btn_close.clicked.connect(self.reject)
