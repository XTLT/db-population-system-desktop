from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogDeleteSelectedHistoryMixin:
    def _delete_selected_history(self):
        """删除选中的就读历史记录（误修改后允许删除错误记录）。"""
        row = self.history_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选中要删除的历史记录！")
            return
        item0 = self.history_table.item(row, 0)
        if not item0:
            return
        history_id = item0.data(Qt.ItemDataRole.UserRole)
        if not history_id:
            QMessageBox.warning(self, "提示", "该记录无法删除（缺少记录标识）！")
            return
        if QMessageBox.question(
            self, "确认删除",
            "确定删除选中的这条就读历史记录吗？\n（只删除历史记录，不影响当前就读信息）",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        ) != QMessageBox.StandardButton.Yes:
            return
        try:
            if get_server_url():
                from network.client import api_delete_education_history
                result = api_delete_education_history(self.person.id, history_id)
                if not result.get('success'):
                    QMessageBox.critical(self, "错误", result.get('error', '删除失败'))
                    return
            else:
                from core.database import delete_education_history as local_delete_history
                if not local_delete_history(history_id):
                    QMessageBox.critical(self, "错误", "删除失败：记录不存在")
                    return
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除失败：{str(e)}")
            return
        self._load_education_data()
