from .._imports import *
from .._consts import *
from ..funcs import *

LandSubsidyImportWorker = None

class LandSubsidyImportDialogSetupUiMixin:
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        font = QFont(FONT_NAME, FONT_SIZE)

        year_layout = QHBoxLayout()
        lbl_year = QLabel("补贴年度：")
        lbl_year.setFont(font)
        self.txt_year_input = QLineEdit()
        self.txt_year_input.setFont(font)
        self.txt_year_input.setPlaceholderText(str(datetime.now().year))
        self.txt_year_input.setText(str(datetime.now().year))
        year_layout.addWidget(lbl_year)
        year_layout.addWidget(self.txt_year_input)
        layout.addLayout(year_layout)

        file_layout = QHBoxLayout()
        self.lbl_file = QLabel("未选择文件")
        self.lbl_file.setFont(font)
        btn_browse = QPushButton("选择文件")
        btn_browse.clicked.connect(self._browse)
        file_layout.addWidget(self.lbl_file)
        file_layout.addWidget(btn_browse)
        layout.addLayout(file_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.lbl_status = QLabel("")
        self.lbl_status.setFont(font)
        layout.addWidget(self.lbl_status)

        btn_layout = QHBoxLayout()
        btn_import = QPushButton("开始导入")
        btn_import.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 10px;")
        btn_import.clicked.connect(self._start_import)
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 10px;")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_import)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
