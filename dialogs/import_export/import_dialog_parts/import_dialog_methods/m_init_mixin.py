from .._imports import *
from .._consts import *
from ..funcs import *

ImportWorker = None

class ImportDialogMInitMixin:
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Excel导入")
        self.setFixedSize(450, 300)
        self.worker = None
        self._setup_ui()
