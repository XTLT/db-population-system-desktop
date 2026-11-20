from .._imports import *
from .._consts import *
from ..funcs import *

from ._attrs import _ColumnSelectDialogAttrsMixin
from .m_init_mixin import _ColumnSelectDialogMInitMixin
from .load_columns_mixin import _ColumnSelectDialogLoadColumnsMixin
from .sheet_name_mixin import _ColumnSelectDialogSheetNameMixin
from .name_col_mixin import _ColumnSelectDialogNameColMixin
from .id_col_mixin import _ColumnSelectDialogIdColMixin

class _ColumnSelectDialog(_ColumnSelectDialogMInitMixin, _ColumnSelectDialogAttrsMixin, _ColumnSelectDialogLoadColumnsMixin, _ColumnSelectDialogSheetNameMixin, _ColumnSelectDialogNameColMixin, _ColumnSelectDialogIdColMixin, QDialog):
    pass
