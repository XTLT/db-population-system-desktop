from .._imports import *
from .._consts import *
from ..funcs import *

LandSubsidyImportWorker = None

class LandSubsidyImportDialogMInitMixin:
    def __init__(self, is_network_mode: bool = False, parent=None):
        super().__init__(parent)
        self.is_network_mode = is_network_mode
        self.setWindowTitle("导入地力补贴")
        self.setFixedSize(450, 250)
        self.worker = None
        self._file_path = ""
        self._setup_ui()
