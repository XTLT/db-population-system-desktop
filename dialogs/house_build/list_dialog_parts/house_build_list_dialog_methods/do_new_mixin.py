from .._imports import *
from .._consts import *
from ..funcs import *
from ...edit_dialog import HouseBuildEditDialog


class HouseBuildListDialogDoNewMixin:
    def _do_new(self):
        if not self.is_network_mode:
            QMessageBox.information(self, "提示", "建房资料保存在服务器，请先连接服务器。")
            return
        dialog = HouseBuildEditDialog(None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_data()
