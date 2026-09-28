from PyQt6.QtWidgets import QLineEdit, QHBoxLayout, QLabel, QTableWidget, QVBoxLayout, QSplitter, QAbstractItemView, QWidget, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.config import FONT_NAME, FONT_SIZE


def _setup_ui(self):
    central = QWidget()
    self.setCentralWidget(central)
    layout = QVBoxLayout(central)

    search_layout = QHBoxLayout()
    lbl_search = QLabel("输入姓名查询：")
    lbl_search.setFont(QFont(FONT_NAME, FONT_SIZE))
    self.txt_search = QLineEdit()
    self.txt_search.setFont(QFont(FONT_NAME, FONT_SIZE))
    self.txt_search.setPlaceholderText("请输入姓名进行模糊查询...")
    self.txt_search.returnPressed.connect(self._do_search)
    btn_search = QPushButton("查询")
    btn_search.setFont(QFont(FONT_NAME, FONT_SIZE))
    btn_search.clicked.connect(self._do_search)
    search_layout.addWidget(lbl_search)
    search_layout.addWidget(self.txt_search)
    search_layout.addWidget(btn_search)
    layout.addLayout(search_layout)

    self.splitter = QSplitter(Qt.Orientation.Vertical)
    self.name_container = QWidget()
    self.name_layout = QVBoxLayout(self.name_container)
    self.name_label = QLabel("")
    self.name_label.setFont(QFont(FONT_NAME, 12))
    self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.name_label.setStyleSheet("background-color: #DDEBF7; font-weight: bold; padding: 8px; border: 1px solid #4472C4;")
    self.name_layout.addWidget(self.name_label)

    self.table = QTableWidget()
    self.table.setFont(QFont(FONT_NAME, FONT_SIZE))
    self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
    self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
    self.table.doubleClicked.connect(self._on_double_click)
    self.table.verticalHeader().setVisible(False)

    self.splitter.addWidget(self.name_container)
    self.splitter.addWidget(self.table)
    self.splitter.setSizes([400, 300])
    layout.addWidget(self.splitter)

    status_layout = QHBoxLayout()
    from core.config import APP_VERSION
    self.lbl_version = QLabel(f"版本：v{APP_VERSION}")
    self.lbl_version.setFont(QFont(FONT_NAME, 9))
    self.lbl_version.setStyleSheet("color: #666;")
    status_layout.addWidget(self.lbl_version)

    self.lbl_status = QLabel("数据库记录数：-")
    self.lbl_status.setFont(QFont(FONT_NAME, 9))
    status_layout.addWidget(self.lbl_status)
    
    self.lbl_backup = QLabel("")
    self.lbl_backup.setFont(QFont(FONT_NAME, 9))
    status_layout.addWidget(self.lbl_backup)
    
    self.lbl_disk = QLabel("")
    self.lbl_disk.setFont(QFont(FONT_NAME, 9))
    status_layout.addWidget(self.lbl_disk)
    
    layout.addLayout(status_layout)
    
    self._refresh_status()
