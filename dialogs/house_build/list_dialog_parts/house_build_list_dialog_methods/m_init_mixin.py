from .._imports import *
from .._consts import *
from ..funcs import *


class HouseBuildListDialogMInitMixin:
    def __init__(self, is_network_mode: bool = True, parent=None):
        super().__init__(parent)
        self.is_network_mode = is_network_mode
        self.items = []
        self.current_app_id = None
        self.setWindowTitle("宅基地建房申请")
        self.setFixedSize(1080, 640)
        self._setup_ui()
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self._load_data)
        if not self.is_network_mode:
            self.lbl_sum.setText("建房资料保存在服务器，请先连接服务器后再使用。")
            return
        try:
            self._load_data()
        except Exception as e:
            QMessageBox.warning(self, "提示", f"加载建房申请时出错：{e}")
