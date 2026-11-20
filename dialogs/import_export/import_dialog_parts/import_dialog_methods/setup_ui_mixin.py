from .._imports import *
from .._consts import *
from ..funcs import *

ImportWorker = None

class ImportDialogSetupUiMixin:
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        from PyQt6.QtGui import QFont
        font = QFont(FONT_NAME, FONT_SIZE)

        mode_label = QLabel("导入模式：")
        mode_label.setFont(font)
        layout.addWidget(mode_label)

        self.radio_full = QRadioButton("全量导入（覆盖所有数据）")
        self.radio_full.setFont(font)
        self.radio_full.setChecked(True)
        self.radio_incremental = QRadioButton("增量导入（新增+更新）")
        self.radio_incremental.setFont(font)
        layout.addWidget(self.radio_full)
        layout.addWidget(self.radio_incremental)

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
        btn_template = QPushButton("生成模板")
        btn_template.clicked.connect(self._generate_template)
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 10px;")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_import)
        btn_layout.addWidget(btn_template)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        self._file_path = ""
