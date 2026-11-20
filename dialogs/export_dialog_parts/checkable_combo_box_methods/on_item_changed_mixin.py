from .._imports import *
from .._consts import *
from ..funcs import *



class CheckableComboBoxOnItemChangedMixin:
    def _on_item_changed(self, state):
        if self._suppress:
            return
        self._suppress = True
        all_checked = all(
            cb.isChecked() for text, cb in self._checkboxes if text != "全部"
        )
        self._checkboxes[0][1].setChecked(all_checked)
        self._suppress = False
        self._update_button()
        self.selectionChanged.emit()
