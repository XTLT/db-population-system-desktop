from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogSetupUiMixin:
    def _setup_ui(self):
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_basic_tab(), "基本信息")
        self.tabs.addTab(self._create_education_tab(), "就读信息")
        layout.addWidget(self.tabs)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("添加家庭成员")
        btn_add.setStyleSheet(f"background-color: {BTN_ADD_COLOR}; color: white; font-weight: bold; padding: 8px;")
        btn_add.clicked.connect(self._add_member)
        btn_layout.addWidget(btn_add)
        layout.addLayout(btn_layout)

        save_layout = QHBoxLayout()
        btn_migrate = QPushButton("户籍迁出")
        btn_migrate.setStyleSheet("background-color: #FF6600; color: white; font-weight: bold; padding: 10px;")
        btn_migrate.clicked.connect(self._migrate_person)
        btn_delete = QPushButton("删除人员")
        btn_delete.setStyleSheet("background-color: #CC0000; color: white; font-weight: bold; padding: 10px;")
        btn_delete.clicked.connect(self._delete_person)
        btn_save = QPushButton("保存修改")
        btn_save.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 10px;")
        btn_save.clicked.connect(self._save)
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 10px;")
        btn_cancel.clicked.connect(self.reject)
        save_layout.addWidget(btn_migrate)
        save_layout.addWidget(btn_delete)
        save_layout.addWidget(btn_save)
        save_layout.addWidget(btn_cancel)
        layout.addLayout(save_layout)
