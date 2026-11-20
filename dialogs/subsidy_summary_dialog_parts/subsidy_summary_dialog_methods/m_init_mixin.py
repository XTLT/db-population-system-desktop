from .._imports import *
from .._consts import *
from ..funcs import *

_HEADERS = None
_LOCAL_MODULES = None
_to_amount = None

class SubsidySummaryDialogMInitMixin:
    def __init__(self, is_network_mode: bool, id_card: str, name: str, parent=None):
        super().__init__(parent)
        self.is_network_mode = is_network_mode
        self.id_card = (id_card or "").strip()
        self.person_name = name or ""
        self.setWindowTitle(f"补贴情况 - {self.person_name}")
        self.setFixedSize(1000, 620)
        self._setup_ui()
        try:
            self._load()
        except Exception as e:
            QMessageBox.warning(self, "提示", f"加载补贴数据时出错：{e}")
