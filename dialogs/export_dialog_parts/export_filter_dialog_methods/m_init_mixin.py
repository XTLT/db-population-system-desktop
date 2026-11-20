from .._imports import *
from .._consts import *
from ..funcs import *

CheckableComboBox = None

class ExportFilterDialogMInitMixin:
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("数据筛选导出")
        # 16 行筛选条件 + 计数 + 按钮，固定 520x470 时底部多行被裁剪成半截字；
        # 自适应高度实测不足（约 590px），显式设为足够大尺寸保证全部可见
        self.setFixedSize(560, 800)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._setup_ui()
