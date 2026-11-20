from .._imports import *
from .._consts import *
from ..funcs import *

FIELD_OPTIONS = None
MATCH_BY_ID_CARD = None
MATCH_BY_NAME = None
_col_letter = None

class ColumnMappingDialogFillMapMixin:
    @property
    def fill_map(self):
        match_col = self.cbo_match_col.currentData()
        result = {}
        for i, combo in enumerate(self._field_combos):
            val = combo.currentData()
            if val and (i + 1) != match_col:
                result[i + 1] = val
        return result
