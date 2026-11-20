from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogReplaceAllMixin:
    def _replace_all(self):
        keyword = self.ed_find.text()
        repl = self.ed_replace.text()
        if not keyword:
            return
        items = self._find_all_items(keyword)
        if not items:
            self.lbl_status.setText(f"未找到「{keyword}」")
            return
        if QMessageBox.question(self, "确认", f"确定将全部 {len(items)} 处「{keyword}」替换为「{repl}」？此操作可撤销。") \
                != QMessageBox.StandardButton.Yes:
            return
        self._push_undo()
        self._suppress_change = True
        try:
            for it in items:
                it.setText(it.text().replace(keyword, repl))
        finally:
            self._suppress_change = False
        self._mark_modified()
        self.lbl_status.setText(f"已替换 {len(items)} 处")
