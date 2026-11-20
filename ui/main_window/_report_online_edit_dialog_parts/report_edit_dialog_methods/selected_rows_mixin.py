from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogSelectedRowsMixin:
    def _selected_rows(self):
        """当前选中区域涉及的行号集合（去重升序）"""
        rows = set()
        for idx in self.table.selectionModel().selectedRows():
            rows.add(idx.row())
        for idx in self.table.selectionModel().selectedIndexes():
            rows.add(idx.row())
        return sorted(rows)
