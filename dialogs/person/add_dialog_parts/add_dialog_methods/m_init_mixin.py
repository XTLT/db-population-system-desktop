from .._imports import *
from .._consts import *
from ..funcs import *



class AddDialogMInitMixin:
    def __init__(self, hu_hao: str, parent=None):
        super().__init__(parent)
        self.hu_hao = hu_hao
        self.setWindowTitle("添加新成员")
        self.setFixedSize(520, 600)
        self._setup_ui()
        self._auto_fill_address()
