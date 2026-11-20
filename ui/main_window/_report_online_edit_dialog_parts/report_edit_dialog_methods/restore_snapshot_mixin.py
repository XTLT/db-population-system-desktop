from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogRestoreSnapshotMixin:
    def _restore_snapshot(self, snap):
        headers, rows = snap
        self._suppress_change = True
        try:
            self._fill_table(headers, rows)
        finally:
            self._suppress_change = False
        self._mark_modified()
