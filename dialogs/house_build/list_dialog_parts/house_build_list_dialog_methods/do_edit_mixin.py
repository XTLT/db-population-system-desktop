from .._imports import *
from .._consts import *
from ..funcs import *
from ...edit_dialog import HouseBuildEditDialog


class HouseBuildListDialogDoEditMixin:
    def _do_edit(self):
        if not self.current_app_id:
            QMessageBox.information(self, "提示", "请先选择一条申请记录。")
            return
        dialog = HouseBuildEditDialog(self.current_app_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_data()
