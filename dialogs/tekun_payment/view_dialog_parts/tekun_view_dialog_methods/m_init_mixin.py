from .._imports import *
from .._consts import *
from ..funcs import *



class TekunViewDialogMInitMixin:
    def __init__(self, is_network_mode: bool = False, is_admin: bool = False, parent=None):
        super().__init__(parent)
        self.is_network_mode = is_network_mode
        self.is_admin = is_admin
        self.setWindowTitle("特困数据")
        self.setFixedSize(1100, 600)
        self._setup_ui()
        try:
            self._load_data()
        except Exception as e:
            QMessageBox.warning(self, "提示", f"加载数据时出错：{e}")
