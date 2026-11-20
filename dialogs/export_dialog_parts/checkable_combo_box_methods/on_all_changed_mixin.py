from .._imports import *
from .._consts import *
from ..funcs import *



class CheckableComboBoxOnAllChangedMixin:
    def _on_all_changed(self, state):
        if self._suppress:
            return
        self._suppress = True
        checked = state == 2
        for text, cb in self._checkboxes:
            if text != "全部":
                cb.setChecked(checked)
        self._suppress = False
        self._update_button()
        self.selectionChanged.emit()
