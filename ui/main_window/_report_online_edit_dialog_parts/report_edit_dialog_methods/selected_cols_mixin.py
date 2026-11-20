from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogSelectedColsMixin:
    def _selected_cols(self):
        cols = set()
        for idx in self.table.selectionModel().selectedColumns():
            cols.add(idx.column())
        for idx in self.table.selectionModel().selectedIndexes():
            cols.add(idx.column())
        return sorted(cols)
