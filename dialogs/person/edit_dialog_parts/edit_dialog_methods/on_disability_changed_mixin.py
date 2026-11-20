from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogOnDisabilityChangedMixin:
    def _on_disability_changed(self, text):
        is_disabled = (text == "是")
        self.cbo_disability_type.setVisible(is_disabled)
        self.cbo_disability_type_label.setVisible(is_disabled)
        self.cbo_dis_level.setVisible(is_disabled)
        self.cbo_dis_level_label.setVisible(is_disabled)
