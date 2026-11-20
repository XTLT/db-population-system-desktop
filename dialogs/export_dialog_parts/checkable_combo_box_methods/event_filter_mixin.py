from .._imports import *
from .._consts import *
from ..funcs import *



class CheckableComboBoxEventFilterMixin:
    def eventFilter(self, obj, event):
        if obj == self._popup and event.type() == QEvent.Type.MouseButtonPress:
            if not self._popup.geometry().contains(event.globalPosition().toPoint()):
                self._popup.hide()
                self._popup_visible = False
        return super().eventFilter(obj, event)
