from .._imports import *
from .._consts import *
from ..funcs import *



class AddDialogDeathDateValueMixin:
    def _death_date_value(self):
        """返回 YYYY-MM-DD；日期停在最小值（1900-01-01）表示未填写。"""
        d = self.dte_death_date.date()
        if d == QDate(1900, 1, 1):
            return ""
        return d.toString("yyyy-MM-dd")
