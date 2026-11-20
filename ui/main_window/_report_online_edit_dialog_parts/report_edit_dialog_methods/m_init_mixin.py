from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogMInitMixin:
    def __init__(self, report_id: str, report_name: str, parent=None):
        super().__init__(parent)
        self.report_id = report_id
        self.report_name = report_name
        self._undo_stack = []      # 快照列表（每项 [headers, rows] 深拷贝）
        self._redo_stack = []
        self._modified = False
        self._suppress_change = False   # 内部填充/恢复时屏蔽 itemChanged
        self._last_find_row = -1        # 查找游标
        self._sheets = []               # 服务端返回的工作表列表
        self._current_sheet = ''        # 当前工作表名
        self._loading = False           # 加载中标志（切换时防重入）
        self.setWindowTitle(f"在线编辑 - {report_name}")
        self.resize(1100, 660)
        # 支持最大化/最小化（默认 QDialog 标题栏无这两个按钮）
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowType.WindowMaximizeButtonHint
            | Qt.WindowType.WindowMinimizeButtonHint
        )
        self._build_ui()
        self._bind_shortcuts()
        self._load_data()
