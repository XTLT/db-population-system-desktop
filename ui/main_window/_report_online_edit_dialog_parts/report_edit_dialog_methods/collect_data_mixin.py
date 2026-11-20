from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogCollectDataMixin:
    def _collect_data(self):
        """收集表头与全部单元格数据（与服务器保存接口约定一致）"""
        headers = []
        for c in range(self.table.columnCount()):
            header_item = self.table.horizontalHeaderItem(c)
            headers.append(header_item.text() if header_item else '')

        rows = []
        for r in range(self.table.rowCount()):
            row = []
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                row.append(item.text() if item else '')
            rows.append(row)
        return headers, rows
