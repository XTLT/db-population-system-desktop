from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogFindAllItemsMixin:
    def _find_all_items(self, keyword):
        return self.table.findItems(keyword, Qt.MatchFlag.MatchContains)
