from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogPushUndoMixin:
    def _push_undo(self):
        snap = copy.deepcopy(self._snapshot())
        self._undo_stack.append(snap)
        if len(self._undo_stack) > UNDO_LIMIT:
            self._undo_stack.pop(0)
        self._redo_stack.clear()
