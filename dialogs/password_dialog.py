from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR


class PasswordDialog(QDialog):
    def __init__(self, is_new: bool = True, parent=None):
        super().__init__(parent)
        self.is_new = is_new
        self.setWindowTitle("数据库密码" if is_new else "输入密码")
        self.setFixedSize(500, 300)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        if self.is_new:
            title = QLabel("设置数据库密码")
            title.setFont(QFont(FONT_NAME, 14, QFont.Weight.Bold))
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet("color: #006600; padding: 10px;")
            layout.addWidget(title)

                    
            warning_box = QLabel(
                "⚠️ 重要警告 ⚠️\n\n"
                "数据库将使用此密码加密。\n"
                "❌ 忘记密码将永久丢失所有数据，无法恢复！\n"
                "❌ 系统无法重置或找回密码！\n\n"
                "请务必牢记密码，建议：\n"
                "• 使用容易记住但不易被猜到的密码\n"
                "• 将密码记录在安全的地方\n"
                "• 定期备份数据库文件（population.db）"
            )
            warning_box.setFont(QFont(FONT_NAME, FONT_SIZE))
            warning_box.setStyleSheet(
                "background-color: #FFF0F0; "
                "padding: 15px; "
                "border: 2px solid #CC0000; "
                "border-radius: 5px;"
            )
            warning_box.setWordWrap(True)
            layout.addWidget(warning_box)
        else:
            title = QLabel("输入数据库密码")
            title.setFont(QFont(FONT_NAME, 12, QFont.Weight.Bold))
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)

            info = QLabel("请输入密码以访问数据库")
            info.setFont(QFont(FONT_NAME, FONT_SIZE))
            info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info)

                
        form_layout = QFormLayout()
        
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("请输入密码")
        form_layout.addRow(QLabel("密码："), self.txt_password)

        if self.is_new:
            self.txt_confirm = QLineEdit()
            self.txt_confirm.setEchoMode(QLineEdit.EchoMode.Password)
            self.txt_confirm.setPlaceholderText("请再次输入密码")
            form_layout.addRow(QLabel("确认密码："), self.txt_confirm)

        layout.addLayout(form_layout)

            
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("确定")
        btn_ok.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 10px;")
        btn_ok.clicked.connect(self._ok)
        
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 10px;")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def get_password(self) -> str:
        return self.txt_password.text()

    def _ok(self):
        password = self.txt_password.text()
        if not password:
            QMessageBox.warning(self, "提示", "密码不能为空！")
            return
        
        if self.is_new:
            if len(password) < 6:
                QMessageBox.warning(self, "提示", "密码长度至少6位！\n\n为了数据安全，请设置更复杂的密码。")
                return
            
            confirm = self.txt_confirm.text()
            if password != confirm:
                QMessageBox.warning(self, "提示", "两次输入的密码不一致！")
                return
            
                  
            reply = QMessageBox.question(
                self, "最终确认",
                "您已牢记此密码了吗？\n\n"
                "⚠️ 忘记密码将永久丢失所有数据！\n"
                "⚠️ 系统无法重置或找回密码！",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        self.accept()
