from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.config import FONT_NAME, BTN_SAVE_COLOR, BTN_CANCEL_COLOR
from core.database import authenticate_user
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user = None
        self.token = None
        self.setWindowTitle("用户登录")
        self.setFixedSize(350, 200)
        self._setup_ui()

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

    def _toggle_password(self):
        if self.chk_show_pw.isChecked():
            self.txt_password.setEchoMode(QLineEdit.EchoMode.Normal)
            self.chk_show_pw.setText("隐藏")
        else:
            self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.chk_show_pw.setText("显示")

    def _login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text()
        if not username or not password:
            QMessageBox.warning(self, "提示", "请输入用户名和密码！")
            return
        
        from network.client import get_server_url
        server_url = get_server_url()
        
        if server_url:
            try:
                from network.client import api_login
                result = api_login(username, password)
                if result.get('success'):
                    self.user = result.get('user')
                    self.token = result.get('token')
                    self.accept()
                else:
                    QMessageBox.warning(self, "错误", result.get('error', '登录失败'))
            except Exception as e:
                QMessageBox.warning(self, "错误", f"登录失败：{str(e)}")
        else:
            try:
                user = authenticate_user(username, password)
                if user:
                    self.user = {
                        'id': user.id,
                        'username': user.username,
                        'real_name': user.real_name,
                        'role': user.role
                    }
                    self.token = "local"
                    self.accept()
                else:
                    from core.database import get_session, User as UserModel
                    sess = get_session()
                    try:
                        u = sess.query(UserModel).filter(UserModel.username == username).first()
                        if u and u.locked_until:
                            from datetime import datetime
                            try:
                                lock_time = datetime.strptime(u.locked_until, "%Y-%m-%d %H:%M:%S")
                                if datetime.now() < lock_time:
                                    remaining = int((lock_time - datetime.now()).total_seconds() / 60) + 1
                                    QMessageBox.warning(self, "账户已锁定", f"密码错误次数过多，账户已锁定。\n请 {remaining} 分钟后重试。")
                                else:
                                    QMessageBox.warning(self, "错误", "用户名或密码错误！")
                            except Exception:
                                QMessageBox.warning(self, "错误", "用户名或密码错误！")
                        else:
                            QMessageBox.warning(self, "错误", "用户名或密码错误！")
                    except Exception:
                        QMessageBox.warning(self, "错误", "用户名或密码错误！")
                    finally:
                        sess.close()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"登录失败：{str(e)}")

    def get_user(self):
        return self.user

    def get_token(self):
        return self.token
class ChangeProfileDialog(QDialog):
    def __init__(self, user_info: dict, parent=None):
        super().__init__(parent)
        self.user_info = user_info
        self.setWindowTitle("账户设置")
        self.setFixedSize(400, 380)
        self._setup_ui()

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

    def _toggle(self):
        if self.chk_show.isChecked():
            self.txt_new_pw.setEchoMode(QLineEdit.EchoMode.Normal)
            self.txt_confirm_pw.setEchoMode(QLineEdit.EchoMode.Normal)
            self.chk_show.setText("隐藏")
        else:
            self.txt_new_pw.setEchoMode(QLineEdit.EchoMode.Password)
            self.txt_confirm_pw.setEchoMode(QLineEdit.EchoMode.Password)
            self.chk_show.setText("显示")

    def _save(self):
        new_username = self.txt_new_username.text().strip()
        real_name = self.txt_real_name.text().strip()
        old_pw = self.txt_old_pw.text()
        new_pw = self.txt_new_pw.text()
        confirm_pw = self.txt_confirm_pw.text()

        if not new_username:
            QMessageBox.warning(self, "提示", "用户名不能为空！")
            return

        from network.client import get_server_url
        server_url = get_server_url()

        if server_url:
            try:
                from network.client import _request
                data = {}
                if new_username != self.user_info.get('username', ''):
                    data['username'] = new_username
                if real_name != self.user_info.get('real_name', ''):
                    data['real_name'] = real_name
                if new_pw:
                    if not old_pw:
                        QMessageBox.warning(self, "提示", "请输入当前密码！")
                        return
                    if new_pw != confirm_pw:
                        QMessageBox.warning(self, "提示", "两次输入的密码不一致！")
                        return
                    data['old_password'] = old_pw
                    data['password'] = new_pw
                if data:
                    result = _request('PUT', f'/api/users/{self.user_info["id"]}', data)
                    if result.get('success'):
                        if new_pw:
                            QMessageBox.information(self, "成功", "密码已修改，程序即将重新启动。")
                            import sys
                            import os
                            os.execl(sys.executable, sys.executable, *sys.argv)
                        else:
                            QMessageBox.information(self, "成功", "账户信息已更新！")
                            self.accept()
                    else:
                        QMessageBox.warning(self, "错误", result.get('error', '修改失败'))
            except Exception as e:
                QMessageBox.warning(self, "错误", f"修改失败：{str(e)}")
        else:
            try:
                if new_username != self.user_info.get('username', ''):
                    from core.database import get_session, User as UserModel
                    sess = get_session()
                    try:
                        existing = sess.query(UserModel).filter(UserModel.username == new_username).first()
                        if existing:
                            QMessageBox.warning(self, "错误", "用户名已存在！")
                            return
                    finally:
                        sess.close()

                if new_pw:
                    if not old_pw:
                        QMessageBox.warning(self, "提示", "请输入当前密码！")
                        return
                    if new_pw != confirm_pw:
                        QMessageBox.warning(self, "提示", "两次输入的密码不一致！")
                        return
                    from core.database import change_user_password
                    ok, msg = change_user_password(self.user_info['id'], old_pw, new_pw)
                    if not ok:
                        QMessageBox.warning(self, "错误", msg)
                        return

                from core.database import update_user
                updates = {}
                if new_username != self.user_info.get('username', ''):
                    updates['username'] = new_username
                if real_name != self.user_info.get('real_name', ''):
                    updates['real_name'] = real_name
                if updates:
                    update_user(self.user_info['id'], **updates)

                if new_pw:
                    QMessageBox.information(self, "成功", "密码已修改，程序即将重新启动。")
                    from core.database import reset_engine, encrypt_database, get_db_password
                    db_pw = get_db_password()
                    if db_pw:
                        reset_engine()
                        encrypt_database(db_pw)
                    import sys
                    import os
                    os.execl(sys.executable, sys.executable, *sys.argv)
                else:
                    QMessageBox.information(self, "成功", "账户信息已更新！")
                    self.accept()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"修改失败：{str(e)}")
