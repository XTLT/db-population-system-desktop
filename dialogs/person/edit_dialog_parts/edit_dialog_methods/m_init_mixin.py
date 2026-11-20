from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogMInitMixin:
    def __init__(self, person: Person, parent=None):
        super().__init__(parent)
        self.person = person
        self.setWindowTitle("编辑家庭成员信息")
        self.setMinimumSize(560, 700)
        self.resize(560, 700)
        self._setup_ui()
        self._load_data()
