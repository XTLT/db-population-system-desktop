from .._imports import *
from .._consts import *
from ..funcs import *



class AddDialogOnIdCardChangedMixin:
    def _on_id_card_changed(self, text):
        age = calculate_age(text)
        if age:
            self.txt_age.setText(age)
