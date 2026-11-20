from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogDeleteRowsMixin:
    def _delete_rows(self):
        sel = self._selected_rows()
        if not sel:
            QMessageBox.information(self, "提示", "请先选中要删除的行")
            return
        if QMessageBox.question(self, "确认", f"确定删除选中的 {len(sel)} 行？此操作可撤销。") \
                != QMessageBox.StandardButton.Yes:
            return
        self._push_undo()
        for r in reversed(sel):
            self.table.removeRow(r)
        self._mark_modified()
        self.lbl_status.setText(f"已删除 {len(sel)} 行")
