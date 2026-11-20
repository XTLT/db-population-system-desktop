from .._imports import *
from .._consts import *
from ..funcs import *



class AddDialogOnIsDeadChangedMixin:
    def _on_is_dead_changed(self, text):
        """选"是"时才显示死亡时间行。"""
        if not hasattr(self, 'lbl_death_date'):
            return
        visible = text == "是"
        self.lbl_death_date.setVisible(visible)
        self.dte_death_date.setVisible(visible)
