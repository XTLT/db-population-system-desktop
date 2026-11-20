from .._imports import *
from .._consts import *
from ..funcs import *

FIELD_OPTIONS = None
MATCH_BY_ID_CARD = None
MATCH_BY_NAME = None
_col_letter = None

class ColumnMappingDialogOnSheetChangedMixin:
    def _on_sheet_changed(self):
        sheet_name = self.cbo_sheet.currentText()
        self._ws = self._wb[sheet_name]
        self.spin_header_row.setMaximum(self._ws.max_row)
        self._on_header_row_changed()
