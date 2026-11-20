from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogDeleteColsMixin:
    def _delete_cols(self):
        sel = self._selected_cols()
        if not sel:
            QMessageBox.information(self, "提示", "请先选中要删除的列")
            return
        if QMessageBox.question(self, "确认", f"确定删除选中的 {len(sel)} 列？此操作可撤销。") \
                != QMessageBox.StandardButton.Yes:
            return
        self._push_undo()
        for c in reversed(sel):
            self.table.removeColumn(c)
        self._mark_modified()
        self.lbl_status.setText(f"已删除 {len(sel)} 列")
