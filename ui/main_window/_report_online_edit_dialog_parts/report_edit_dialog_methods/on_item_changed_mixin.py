from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogOnItemChangedMixin:
    def _on_item_changed(self, _item):
        if self._suppress_change:
            return
        # 单元格编辑提交时入撤销栈（编辑期间不去抖：QTableWidget 在编辑提交时才发一次）
        self._push_undo()
        self._mark_modified()
