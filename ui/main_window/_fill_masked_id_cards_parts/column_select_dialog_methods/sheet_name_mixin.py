from .._imports import *
from .._consts import *
from ..funcs import *



class _ColumnSelectDialogSheetNameMixin:
    @property
    def sheet_name(self):
        return self.cb_sheet.currentText()
