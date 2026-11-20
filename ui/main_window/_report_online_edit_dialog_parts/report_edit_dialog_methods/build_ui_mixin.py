from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogBuildUiMixin:
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # 工具栏
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("工作表："))
        self.combo_sheet = QComboBox()
        self.combo_sheet.setFixedWidth(160)
        self.combo_sheet.setToolTip("切换当前编辑的工作表（多工作表报表）")
        self.combo_sheet.currentTextChanged.connect(self._on_sheet_changed)
        toolbar.addWidget(self.combo_sheet)
        toolbar.addSpacing(10)
        for text, tip, slot in (
            ("插入行", "在选中行上方插入行（多选插入多行，无选中在末尾追加）", self._insert_rows),
            ("删除行", "删除选中的行（支持多行）", self._delete_rows),
            ("插入列", "在选中列左侧插入列（多选插入多列，无选中在末尾追加）", self._insert_cols),
            ("删除列", "删除选中的列（支持多列）", self._delete_cols),
            ("撤销", "撤销上一步操作 (Ctrl+Z)", self._undo),
            ("重做", "重做被撤销的操作 (Ctrl+Y)", self._redo),
        ):
            btn = QPushButton(text)
            btn.setToolTip(tip)
            btn.setStyleSheet("padding: 5px 14px;")
            btn.clicked.connect(slot)
            toolbar.addWidget(btn)
        toolbar.addStretch()

        self.btn_save = QPushButton("保存")
        self.btn_save.setStyleSheet(
            f"background-color: {BTN_ADD_COLOR}; color: white; font-weight: bold; padding: 5px 18px;"
        )
        self.btn_save.clicked.connect(self._save)
        toolbar.addWidget(self.btn_save)
        btn_close = QPushButton("关闭")
        btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 5px 14px;")
        btn_close.clicked.connect(self.reject)
        toolbar.addWidget(btn_close)
        layout.addLayout(toolbar)

        # 查找/替换栏
        findbox = QGroupBox("查找 / 替换")
        fh = QHBoxLayout(findbox)
        fh.setContentsMargins(8, 4, 8, 4)
        fh.addWidget(QLabel("查找："))
        self.ed_find = QLineEdit()
        self.ed_find.setPlaceholderText("输入要查找的内容")
        self.ed_find.setFixedWidth(220)
        self.ed_find.returnPressed.connect(self._find_next)
        fh.addWidget(self.ed_find)
        btn_find_next = QPushButton("查找下一个")
        btn_find_next.clicked.connect(self._find_next)
        fh.addWidget(btn_find_next)
        fh.addSpacing(12)
        fh.addWidget(QLabel("替换为："))
        self.ed_replace = QLineEdit()
        self.ed_replace.setPlaceholderText("替换后的内容")
        self.ed_replace.setFixedWidth(220)
        fh.addWidget(self.ed_replace)
        btn_replace = QPushButton("替换")
        btn_replace.clicked.connect(self._replace_once)
        fh.addWidget(btn_replace)
        btn_replace_all = QPushButton("全部替换")
        btn_replace_all.clicked.connect(self._replace_all)
        fh.addWidget(btn_replace_all)
        fh.addStretch()
        layout.addWidget(findbox)

        # 表格
        self.table = QTableWidget()
        self.table.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
            | QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.table, 1)

        # 状态栏
        self.lbl_status = QLabel("正在加载报表数据...")
        self.lbl_status.setStyleSheet("color: #666; font-size: 13px; padding: 4px 0;")
        layout.addWidget(self.lbl_status)
