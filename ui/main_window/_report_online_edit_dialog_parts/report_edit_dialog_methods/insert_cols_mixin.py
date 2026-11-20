from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogInsertColsMixin:
    def _insert_cols(self):
        self._push_undo()
        sel = self._selected_cols()
        n = len(sel) if sel else 1
        anchor = sel[0] if sel else self.table.columnCount()
        self.table.insertColumn(anchor)
        for _ in range(n - 1):
            self.table.insertColumn(anchor)
        self._mark_modified()
        self.lbl_status.setText(f"已插入 {n} 列")
