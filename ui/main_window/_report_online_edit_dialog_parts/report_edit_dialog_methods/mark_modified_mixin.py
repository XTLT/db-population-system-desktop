from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogMarkModifiedMixin:
    def _mark_modified(self):
        self._modified = True
        self.btn_save.setStyleSheet(
            f"background-color: #E67E22; color: white; font-weight: bold; padding: 5px 18px;"
        )
