from .._imports import *
from .._consts import *
from ..funcs import *


class HouseBuildEditDialogMInitMixin:
    def __init__(self, app_id=None, parent=None):
        super().__init__(parent)
        self.app_id = app_id
        self.data = None
        self.setWindowTitle("宅基地建房申请" if app_id else "新建宅基地建房申请")
        self.resize(980, 760)
        self._setup_ui()
        if app_id:
            try:
                self._load_data()
            except Exception as e:
                QMessageBox.warning(self, "提示", f"加载申请详情失败：{e}")
                self.reject()
