from .._imports import *
from .._consts import *
from ..funcs import *



class ChangeProfileDialogMInitMixin:
    def __init__(self, user_info: dict, parent=None):
        super().__init__(parent)
        self.user_info = user_info
        self.setWindowTitle("账户设置")
        self.setFixedSize(400, 380)
        self._setup_ui()
