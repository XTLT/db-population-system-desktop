from .._imports import *
from .._consts import *
from ..funcs import *



class StudentQueryDialogSetupUiMixin:
    def _setup_ui(self):
        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("学校："))
        self.txt_school = QLineEdit()
        self.txt_school.setPlaceholderText("全部")
        filter_layout.addWidget(self.txt_school)

        filter_layout.addWidget(QLabel("年级："))
        self.cbo_grade = QComboBox()
        self.cbo_grade.addItem("")
        for g in GRADES:
            self.cbo_grade.addItem(GRADE_DISPLAY.get(g, g), g)
        filter_layout.addWidget(self.cbo_grade)

        filter_layout.addWidget(QLabel("班级："))
        self.txt_class = QLineEdit()
        self.txt_class.setPlaceholderText("全部")
        filter_layout.addWidget(self.txt_class)

        filter_layout.addWidget(QLabel("留守儿童："))
        self.cbo_left_behind = QComboBox()
        self.cbo_left_behind.addItems(["", "是", "否"])
        filter_layout.addWidget(self.cbo_left_behind)

        btn_search = QPushButton("查询")
        btn_search.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 8px;")
        btn_search.clicked.connect(self._search)
        filter_layout.addWidget(btn_search)

        btn_select_all = QPushButton("全选")
        btn_select_all.clicked.connect(self._select_all)
        filter_layout.addWidget(btn_select_all)

        btn_deselect_all = QPushButton("取消全选")
        btn_deselect_all.clicked.connect(self._deselect_all)
        filter_layout.addWidget(btn_deselect_all)
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        batch_layout = QHBoxLayout()
        batch_layout.addWidget(QLabel("批量设置学校："))
        self.txt_batch_school = QLineEdit()
        batch_layout.addWidget(self.txt_batch_school)
        btn_batch_school = QPushButton("应用")
        btn_batch_school.clicked.connect(self._batch_school)
        batch_layout.addWidget(btn_batch_school)

        batch_layout.addWidget(QLabel("留守儿童："))
        self.cbo_batch_left = QComboBox()
        self.cbo_batch_left.addItems(["是", "否"])
        batch_layout.addWidget(self.cbo_batch_left)
        btn_batch_left = QPushButton("批量设置")
        btn_batch_left.clicked.connect(self._batch_left_behind)
        batch_layout.addWidget(btn_batch_left)
        layout.addLayout(batch_layout)
