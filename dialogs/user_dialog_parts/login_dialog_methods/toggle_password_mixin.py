from .._imports import *
from .._consts import *
from ..funcs import *



class LoginDialogTogglePasswordMixin:
    def _toggle_password(self):
        if self.chk_show_pw.isChecked():
            self.txt_password.setEchoMode(QLineEdit.EchoMode.Normal)
            self.chk_show_pw.setText("隐藏")
        else:
            self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.chk_show_pw.setText("显示")
