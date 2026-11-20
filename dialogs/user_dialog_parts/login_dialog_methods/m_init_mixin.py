from .._imports import *
from .._consts import *
from ..funcs import *



class LoginDialogMInitMixin:
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user = None
        self.token = None
        self.setWindowTitle("用户登录")
        self.setFixedSize(350, 200)
        self._setup_ui()
