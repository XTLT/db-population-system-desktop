from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogAddMemberMixin:
    def _add_member(self):
        from dialogs.person.add_dialog import AddDialog
        hu_hao = self.person.hu_hao
        dialog = AddDialog(hu_hao, self)
        if dialog.exec():
            self.accept()
