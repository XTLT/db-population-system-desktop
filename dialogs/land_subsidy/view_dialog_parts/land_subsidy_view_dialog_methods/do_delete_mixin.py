from .._imports import *
from .._consts import *
from ..funcs import *



class LandSubsidyViewDialogDoDeleteMixin:
    def _do_delete(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "提示", "请选择要删除的记录")
            return
        row = selected[0].row()
        subsidy_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除这条记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.is_network_mode:
                try:
                    from network.client import _request
                    _request('DELETE', f'/api/land_subsidy/{subsidy_id}')
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"删除失败：{e}")
                    return
            else:
                from data.excel_importer import delete_land_subsidy
                delete_land_subsidy(subsidy_id)
            self._load_data()
