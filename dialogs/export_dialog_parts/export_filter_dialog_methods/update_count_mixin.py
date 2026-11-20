from .._imports import *
from .._consts import *
from ..funcs import *

CheckableComboBox = None

class ExportFilterDialogUpdateCountMixin:
    def update_count(self, count: int):
        self.lbl_count.setText(f"当前符合条件：共 {count} 条记录")
