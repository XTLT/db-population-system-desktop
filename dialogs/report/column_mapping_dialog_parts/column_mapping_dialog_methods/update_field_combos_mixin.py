from .._imports import *
from .._consts import *
from ..funcs import *

FIELD_OPTIONS = None
MATCH_BY_ID_CARD = None
MATCH_BY_NAME = None
_col_letter = None

class ColumnMappingDialogUpdateFieldCombosMixin:
    def _update_field_combos(self):
        match_by = self.cbo_match.currentData()
        for combo in self._field_combos:
            for i in range(combo.count()):
                combo.model().item(i).setEnabled(combo.itemData(i) != match_by)
