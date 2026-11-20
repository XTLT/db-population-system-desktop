from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogFindNextMixin:
    def _find_next(self):
        keyword = self.ed_find.text()
        if not keyword:
            return
        items = self._find_all_items(keyword)
        if not items:
            self.lbl_status.setText(f"未找到「{keyword}」")
            self._last_find_row = -1
            return
        # 从上次位置之后循环
        start = self._last_find_row + 1
        target = None
        for it in items:
            if it.row() >= start:
                target = it
                break
        if target is None:
            target = items[0]
        self.table.setCurrentCell(target.row(), target.column())
        self.table.setFocus()
        self._last_find_row = target.row()
        self.lbl_status.setText(f"找到第 {target.row() + 1} 行第 {target.column() + 1} 列")
