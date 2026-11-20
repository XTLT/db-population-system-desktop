from .._imports import *
from .._consts import *
from ..funcs import *

FIELD_OPTIONS = None
MATCH_BY_ID_CARD = None
MATCH_BY_NAME = None
_col_letter = None

class ColumnMappingDialogMatchColMixin:
    @property
    def match_col(self):
        return self.cbo_match_col.currentData()
