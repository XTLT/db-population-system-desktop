from .._imports import *
from .._consts import *
from ..funcs import *



class CheckableComboBoxUpdateButtonMixin:
    def _update_button(self):
        selected = self.get_selected()
        if not selected:
            self._btn.setText("全部")
        elif len(selected) <= 2:
            self._btn.setText("、".join(selected))
        else:
            self._btn.setText(f"{selected[0]}、{selected[1]}等{len(selected)}项")
