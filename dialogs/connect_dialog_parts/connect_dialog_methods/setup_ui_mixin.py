from .._imports import *
from .._consts import *
from ..funcs import *

ServerScanner = None
get_recent_servers = None
save_recent_server = None

class ConnectDialogSetupUiMixin:
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("连接到服务器")
        title.setFont(QFont(FONT_NAME, 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 自动搜索按钮
        self.btn_scan = QPushButton("🔍 自动搜索局域网服务器")
        self.btn_scan.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.btn_scan.setStyleSheet("""
            QPushButton {
                background-color: #0078D4;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
            QPushButton:disabled {
                background-color: #999;
            }
        """)
        self.btn_scan.clicked.connect(self._start_scan)
        layout.addWidget(self.btn_scan)

        # 扫描状态标签
        self.lbl_status = QLabel("")
        self.lbl_status.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("color: #666;")
        self.lbl_status.setVisible(False)
        layout.addWidget(self.lbl_status)

        # 分隔线
        separator = QLabel("─" * 20 + " 或 " + "─" * 20)
        separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        separator.setStyleSheet("color: #999;")
        layout.addWidget(separator)

        # 手动输入
        self.lbl_input = QLabel("输入服务器地址：")
        self.lbl_input.setFont(QFont(FONT_NAME, FONT_SIZE))
        layout.addWidget(self.lbl_input)

        self.cmb_server = QComboBox()
        self.cmb_server.setEditable(True)
        self.cmb_server.setPlaceholderText("https://服务器IP:端口 或 域名")
        self.cmb_server.setFont(QFont(FONT_NAME, FONT_SIZE))
        
        recent = get_recent_servers()
        if recent:
            self.cmb_server.addItems(recent)
            # 自动填入最近一次成功输入的服务器地址，旧地址保留在下拉历史中
            self.cmb_server.setEditText(recent[0])
        
        layout.addWidget(self.cmb_server)

        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_connect = QPushButton("连接")
        self.btn_connect.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.btn_connect.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 10px 30px;")
        self.btn_connect.clicked.connect(self._connect)
        btn_layout.addWidget(self.btn_connect)

        btn_local = QPushButton("本地模式")
        btn_local.setFont(QFont(FONT_NAME, FONT_SIZE))
        btn_local.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 10px 20px;")
        btn_local.clicked.connect(self._local_mode)
        btn_layout.addWidget(btn_local)

        layout.addLayout(btn_layout)
