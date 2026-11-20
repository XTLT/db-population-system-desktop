from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogReplaceOnceMixin:
    def _replace_once(self):
        keyword = self.ed_find.text()
        repl = self.ed_replace.text()
        if not keyword:
            return
        self._find_next()
        idx = self.table.currentIndex()
        if idx.isValid():
            item = self.table.item(idx.row(), idx.column())
            if item and keyword in item.text():
                self._push_undo()
                self._suppress_change = True
                try:
                    item.setText(item.text().replace(keyword, repl, 1))
                finally:
                    self._suppress_change = False
                self._mark_modified()
                self.lbl_status.setText("已替换 1 处")
