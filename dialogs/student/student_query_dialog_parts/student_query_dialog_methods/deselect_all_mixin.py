from .._imports import *
from .._consts import *
from ..funcs import *



class StudentQueryDialogDeselectAllMixin:
    def _deselect_all(self):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(Qt.CheckState.Unchecked)
