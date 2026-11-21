from .._imports import *
from .._consts import *
from ..funcs import *


class HouseBuildEditDialogSetupUiMixin:
    def _setup_ui(self):
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        lbl_no = QLabel("申请编号：")
        lbl_no.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_app_no = QLineEdit()
        self.txt_app_no.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_app_no.setReadOnly(True)
        self.txt_app_no.setPlaceholderText("保存后自动生成")
        self.txt_app_no.setFixedWidth(140)

        lbl_status = QLabel("状态：")
        lbl_status.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.cmb_status = QComboBox()
        self.cmb_status.setFont(QFont(FONT_NAME, FONT_SIZE))
        for value, text in STATUS_OPTIONS:
            self.cmb_status.addItem(text, value)

        lbl_id = QLabel("申请人身份证：")
        lbl_id.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_id_card = QLineEdit()
        self.txt_id_card.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_id_card.setFixedWidth(200)
        self.txt_id_card.setPlaceholderText("输入身份证号")
        btn_prefill = QPushButton("从人口库带出")
        btn_prefill.setStyleSheet("padding: 6px 10px;")

        top.addWidget(lbl_no)
        top.addWidget(self.txt_app_no)
        top.addWidget(lbl_status)
        top.addWidget(self.cmb_status)
        top.addSpacing(12)
        top.addWidget(lbl_id)
        top.addWidget(self.txt_id_card)
        top.addWidget(btn_prefill)
        top.addStretch()
        layout.addLayout(top)

        self.lbl_history = QLabel("")
        self.lbl_history.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.lbl_history.setStyleSheet("color: #888888;")
        layout.addWidget(self.lbl_history)

        self.tabs = QTabWidget()
        self.tabs.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.tab_apply = QWidget()
        self.tab_approval = QWidget()
        self._setup_apply_tab()
        self._setup_approval_tab()
        self.tabs.addTab(self.tab_apply, "农村宅基地和建房(规划许可)申请表")
        self.tabs.addTab(self.tab_approval, "农村宅基地和建房(规划许可)审批表")
        layout.addWidget(self.tabs, 1)

        btn_layout = QHBoxLayout()
        btn_xlsx = QPushButton("导出Excel")
        btn_xlsx.setStyleSheet("padding: 8px;")
        btn_pdf = QPushButton("导出PDF")
        btn_pdf.setStyleSheet("padding: 8px;")
        btn_save = QPushButton("保存")
        btn_save.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; padding: 8px 20px;")
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px 20px;")

        btn_layout.addWidget(btn_xlsx)
        btn_layout.addWidget(btn_pdf)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        btn_prefill.clicked.connect(self._on_prefill)
        btn_save.clicked.connect(self._save)
        btn_cancel.clicked.connect(self.reject)
        btn_xlsx.clicked.connect(lambda: self._do_export('xlsx'))
        btn_pdf.clicked.connect(lambda: self._do_export('pdf'))
