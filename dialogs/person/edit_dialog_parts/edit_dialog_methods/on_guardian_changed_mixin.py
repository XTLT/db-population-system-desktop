from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogOnGuardianChangedMixin:
    def _on_guardian_changed(self, index):
        phone = self.cbo_guardian.currentData()
        if phone and phone != "无":
            self.txt_guardian_phone.setText(phone)
