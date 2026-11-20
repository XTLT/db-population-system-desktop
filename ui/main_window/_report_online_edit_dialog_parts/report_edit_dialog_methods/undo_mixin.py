from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogUndoMixin:
    def _undo(self):
        if not self._undo_stack:
            self.lbl_status.setText("没有可撤销的操作")
            return
        self._redo_stack.append(copy.deepcopy(self._snapshot()))
        snap = self._undo_stack.pop()
        self._restore_snapshot(snap)
        self.lbl_status.setText("已撤销")
