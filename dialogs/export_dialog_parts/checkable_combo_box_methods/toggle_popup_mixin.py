from .._imports import *
from .._consts import *
from ..funcs import *



class CheckableComboBoxTogglePopupMixin:
    def _toggle_popup(self):
        if self._popup_visible:
            self._popup.hide()
            self._popup_visible = False
        else:
            pos = self._btn.mapToGlobal(self._btn.rect().bottomLeft())
            self._popup.move(pos)
            self._popup.show()
            self._popup_visible = True
