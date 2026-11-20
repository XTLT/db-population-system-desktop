from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogInsertRowsMixin:
    def _insert_rows(self):
        self._push_undo()
        sel = self._selected_rows()
        n = len(sel) if sel else 1
        anchor = sel[0] if sel else self.table.rowCount()   # 无选中 → 末尾追加
        self.table.insertRow(anchor)
        for _ in range(n - 1):
            self.table.insertRow(anchor)
        self._mark_modified()
        self.lbl_status.setText(f"已插入 {n} 行")
