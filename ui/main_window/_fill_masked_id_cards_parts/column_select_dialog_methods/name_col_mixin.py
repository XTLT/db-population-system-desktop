from .._imports import *
from .._consts import *
from ..funcs import *



class _ColumnSelectDialogNameColMixin:
    @property
    def name_col(self):
        return self.cb_name.currentText()
