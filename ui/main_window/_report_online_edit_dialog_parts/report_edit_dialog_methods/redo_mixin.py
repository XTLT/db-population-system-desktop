from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogRedoMixin:
    def _redo(self):
        if not self._redo_stack:
            self.lbl_status.setText("没有可重做的操作")
            return
        self._undo_stack.append(copy.deepcopy(self._snapshot()))
        snap = self._redo_stack.pop()
        self._restore_snapshot(snap)
        self.lbl_status.setText("已重做")
