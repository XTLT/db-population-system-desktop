from .._imports import *
from .._consts import *
from ..funcs import *


class HouseBuildListDialogDoDeleteMixin:
    def _do_delete(self):
        if not self.current_app_id:
            QMessageBox.information(self, "提示", "请先选择一条申请记录。")
            return
        row = self.table.currentRow()
        name = ''
        if 0 <= row < len(self.items):
            name = self.items[row].get('owner_name', '')
        if QMessageBox.question(
            self, "确认删除",
            '确定删除「%s」的这条建房申请吗？删除后无法恢复。' % (name or '该记录'),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:
            return
        try:
            api_house_build_delete(self.current_app_id)
        except Exception as e:
            QMessageBox.warning(self, "提示", f"删除失败：{e}")
            return
        QMessageBox.information(self, "完成", "已删除该条建房申请。")
        self._load_data()
