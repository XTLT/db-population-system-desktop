from .._imports import *
from .._consts import *
from ..funcs import *

FIELD_OPTIONS = None
MATCH_BY_ID_CARD = None
MATCH_BY_NAME = None
_col_letter = None

class ColumnMappingDialogMInitMixin:
    def __init__(self, wb, parent=None):
        super().__init__(parent)
        self.setWindowTitle("列映射设置")
        self.setMinimumSize(650, 520)
        self._wb = wb
        self._ws = wb.active
        self._headers = []
        self._field_combos = []
        self._setup_ui()
        self._on_sheet_changed()
