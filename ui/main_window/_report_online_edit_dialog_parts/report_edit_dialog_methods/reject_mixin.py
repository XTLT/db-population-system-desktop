from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogRejectMixin:
    def reject(self):
        if self._modified:
            ret = QMessageBox.question(
                self, "未保存修改",
                "报表有未保存的修改，关闭将丢失这些修改。\n\n确定要关闭吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if ret != QMessageBox.StandardButton.Yes:
                return
        super().reject()
