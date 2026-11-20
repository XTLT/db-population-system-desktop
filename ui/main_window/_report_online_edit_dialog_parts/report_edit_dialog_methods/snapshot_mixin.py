from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogSnapshotMixin:
    def _snapshot(self):
        headers = []
        for c in range(self.table.columnCount()):
            hi = self.table.horizontalHeaderItem(c)
            headers.append(hi.text() if hi else '')
        rows = []
        for r in range(self.table.rowCount()):
            row = []
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                row.append(item.text() if item else '')
            rows.append(row)
        return [headers, rows]
