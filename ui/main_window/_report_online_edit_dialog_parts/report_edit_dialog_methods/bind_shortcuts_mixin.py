from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogBindShortcutsMixin:
    def _bind_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Z"), self, activated=self._undo)
        QShortcut(QKeySequence("Ctrl+Y"), self, activated=self._redo)
        QShortcut(QKeySequence("Ctrl+F"), self, activated=lambda: self.ed_find.setFocus())
