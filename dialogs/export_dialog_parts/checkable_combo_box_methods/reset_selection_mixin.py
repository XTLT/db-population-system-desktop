from .._imports import *
from .._consts import *
from ..funcs import *



class CheckableComboBoxResetSelectionMixin:
    def reset_selection(self):
        self._suppress = True
        self._checkboxes[0][1].setChecked(True)
        for text, cb in self._checkboxes:
            if text != "全部":
                cb.setChecked(False)
        self._suppress = False
        self._update_button()
