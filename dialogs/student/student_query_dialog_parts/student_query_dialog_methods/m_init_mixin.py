from .._imports import *
from .._consts import *
from ..funcs import *



class StudentQueryDialogMInitMixin:
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("学生信息查询")
        self.setMinimumSize(1000, 600)
        self._setup_ui()
        self._load_data()
