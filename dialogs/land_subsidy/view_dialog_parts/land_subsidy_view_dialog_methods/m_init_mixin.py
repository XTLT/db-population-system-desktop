from .._imports import *
from .._consts import *
from ..funcs import *



class LandSubsidyViewDialogMInitMixin:
    def __init__(self, is_network_mode: bool = False, is_admin: bool = False, parent=None):
        super().__init__(parent)
        self.is_network_mode = is_network_mode
        self.is_admin = is_admin
        self.filter_id_card = None
        self.setWindowTitle("地力补贴数据")
        self.setFixedSize(1000, 600)
        self._setup_ui()
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self._load_data)
        try:
            self._load_years()
            self._load_data()
        except Exception as e:
            QMessageBox.warning(self, "提示", f"加载数据时出错：{e}")
