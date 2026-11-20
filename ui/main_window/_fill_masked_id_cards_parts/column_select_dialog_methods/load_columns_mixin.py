from .._imports import *
from .._consts import *
from ..funcs import *



class _ColumnSelectDialogLoadColumnsMixin:
    def _load_columns(self, sheet_name):
        ws = self._wb[sheet_name]
        headers = []
        for cell in ws[1]:
            v = str(cell.value or '').strip()
            if v and v not in headers:
                headers.append(v)
        self.cb_name.clear()
        self.cb_id.clear()
        self.cb_name.addItem("（未找到姓名列）") if not headers else None
        self.cb_id.addItem("（未找到证件号码列）") if not headers else None
        for h in headers:
            self.cb_name.addItem(h)
            self.cb_id.addItem(h)
        # 自动预选匹配的表头
        for i, h in enumerate(headers):
            if h in self.NAME_COLS:
                self.cb_name.setCurrentIndex(i)
            if h in self.ID_COLS:
                self.cb_id.setCurrentIndex(i)
