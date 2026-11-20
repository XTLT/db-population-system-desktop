from .._imports import *
from .._consts import *
from ..funcs import *

DisabilityCareImportWorker = None

class DisabilityCareImportDialogMInitMixin:
    def __init__(self, is_network_mode: bool = False, parent=None):
        super().__init__(parent)
        self.is_network_mode = is_network_mode
        self.setWindowTitle("导入残疾人护理补贴数据")
        self.setFixedSize(450, 300)
        self.worker = None
        self._file_path = ""
        self._setup_ui()
