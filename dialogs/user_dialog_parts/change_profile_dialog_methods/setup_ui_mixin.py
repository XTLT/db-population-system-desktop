from .._imports import *
from .._consts import *
from ..funcs import *



class ChangeProfileDialogSetupUiMixin:
    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("账户设置")
        title.setFont(QFont(FONT_NAME, 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        tabs_layout = QVBoxLayout()

        tabs_layout.addWidget(QLabel("─── 修改用户名 ───"))
        form1 = QFormLayout()
        self.txt_new_username = QLineEdit()
        self.txt_new_username.setText(self.user_info.get('username', ''))
        form1.addRow(QLabel("新用户名："), self.txt_new_username)
        self.txt_real_name = QLineEdit()
        self.txt_real_name.setText(self.user_info.get('real_name', ''))
        form1.addRow(QLabel("真实姓名："), self.txt_real_name)
        tabs_layout.addLayout(form1)

        tabs_layout.addWidget(QLabel("─── 修改密码 ───"))
        form2 = QFormLayout()
        self.txt_old_pw = QLineEdit()
        self.txt_old_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_old_pw.setPlaceholderText("请输入当前密码")
        form2.addRow(QLabel("当前密码："), self.txt_old_pw)

        pw_layout = QHBoxLayout()
        self.txt_new_pw = QLineEdit()
        self.txt_new_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_new_pw.setPlaceholderText("至少8位，含字母和数字")
        self.chk_show = QPushButton("显示")
        self.chk_show.setFixedWidth(45)
        self.chk_show.setCheckable(True)
        self.chk_show.clicked.connect(self._toggle)
        pw_layout.addWidget(self.txt_new_pw)
        pw_layout.addWidget(self.chk_show)
        form2.addRow(QLabel("新密码："), pw_layout)

        self.txt_confirm_pw = QLineEdit()
        self.txt_confirm_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_confirm_pw.setPlaceholderText("再次输入新密码")
        form2.addRow(QLabel("确认密码："), self.txt_confirm_pw)
        tabs_layout.addLayout(form2)

        layout.addLayout(tabs_layout)

        btn_layout = QHBoxLayout()
        btn_save = QPushButton("保存")
        btn_save.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 8px;")
        btn_save.clicked.connect(self._save)
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px;")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
