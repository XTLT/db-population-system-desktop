from .._imports import *
from .._consts import *
from ..funcs import *



class LoginDialogSetupUiMixin:
    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("用户登录")
        title.setFont(QFont(FONT_NAME, 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("请输入用户名")
        form.addRow(QLabel("用户名："), self.txt_username)

        pw_layout = QHBoxLayout()
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("请输入密码")
        self.txt_password.returnPressed.connect(self._login)
        self.chk_show_pw = QPushButton("显示")
        self.chk_show_pw.setFixedWidth(45)
        self.chk_show_pw.setCheckable(True)
        self.chk_show_pw.clicked.connect(self._toggle_password)
        pw_layout.addWidget(self.txt_password)
        pw_layout.addWidget(self.chk_show_pw)
        form.addRow(QLabel("密码："), pw_layout)

        self.lbl_lock = QLabel("")
        self.lbl_lock.setStyleSheet("color: red;")
        form.addRow("", self.lbl_lock)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_login = QPushButton("登录")
        btn_login.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 8px;")
        btn_login.clicked.connect(self._login)
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px;")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_login)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
