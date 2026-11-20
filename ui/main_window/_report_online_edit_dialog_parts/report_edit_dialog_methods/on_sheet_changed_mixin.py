from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogOnSheetChangedMixin:
    def _on_sheet_changed(self, name):
        if self._loading or not name or name == self._current_sheet:
            return
        if self._modified:
            ret = QMessageBox.question(
                self, "未保存修改",
                f"当前工作表「{self._current_sheet}」有未保存的修改，切换后将丢失这些修改。\n\n确定要切换到「{name}」吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if ret != QMessageBox.StandardButton.Yes:
                self.combo_sheet.blockSignals(True)
                self.combo_sheet.setCurrentText(self._current_sheet)
                self.combo_sheet.blockSignals(False)
                return
        self._load_data(sheet=name)
