from .._imports import *
from .._consts import *
from ..funcs import *



class ChangeProfileDialogToggleMixin:
    def _toggle(self):
        if self.chk_show.isChecked():
            self.txt_new_pw.setEchoMode(QLineEdit.EchoMode.Normal)
            self.txt_confirm_pw.setEchoMode(QLineEdit.EchoMode.Normal)
            self.chk_show.setText("隐藏")
        else:
            self.txt_new_pw.setEchoMode(QLineEdit.EchoMode.Password)
            self.txt_confirm_pw.setEchoMode(QLineEdit.EchoMode.Password)
            self.chk_show.setText("显示")
