from .._imports import *
from .._consts import *
from ..funcs import *



class _ColumnSelectDialogIdColMixin:
    @property
    def id_col(self):
        return self.cb_id.currentText()
