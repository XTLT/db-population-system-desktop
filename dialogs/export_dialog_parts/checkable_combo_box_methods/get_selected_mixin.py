from .._imports import *
from .._consts import *
from ..funcs import *



class CheckableComboBoxGetSelectedMixin:
    def get_selected(self):
        if self._checkboxes[0][1].isChecked():
            return []
        return [text for text, cb in self._checkboxes if text != "全部" and cb.isChecked()]
