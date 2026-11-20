from .._imports import *
from .._consts import *
from ..funcs import *

GradePromotionWorker = None

class GradePromotionDialogMInitMixin:
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("年级升级")
        self.setFixedSize(400, 200)
        self.worker = None
        self.is_network = bool(get_server_url())
        self._setup_ui()
