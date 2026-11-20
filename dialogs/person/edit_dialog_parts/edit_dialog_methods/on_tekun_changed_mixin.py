from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogOnTekunChangedMixin:
    def _on_tekun_changed(self, text):
        is_tekun = (text == "是")
        self.cbo_tekun_type.setVisible(is_tekun)
        self.cbo_tekun_type_label.setVisible(is_tekun)
