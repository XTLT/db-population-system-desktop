from .._imports import *
from .._consts import *
from ..funcs import *

ElderlyAllowanceImportWorker = None

class ElderlyAllowanceImportDialogMInitMixin:
    def __init__(self, is_network_mode: bool = False, parent=None):
        super().__init__(parent)
        self.is_network_mode = is_network_mode
        self.setWindowTitle("导入高龄补贴数据")
        self.setFixedSize(450, 300)
        self.worker = None
        self._file_path = ""
        self._setup_ui()
