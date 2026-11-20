from .._imports import *
from .._consts import *
from ..funcs import *



class DibaoViewDialogDoDeleteMixin:
    def _do_delete(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "提示", "请先选择要删除的记录")
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除选中的 {len(selected) // self.table.columnCount()} 条记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            rows = set()
            for item in selected:
                rows.add(item.row())

            row_ids = []
            for row in rows:
                id_item = self.table.item(row, 1)
                if id_item:
                    row_ids.append(id_item.data(Qt.ItemDataRole.UserRole))

            if self.is_network_mode:
                from network.client import _request
                for rid in row_ids:
                    if rid:
                        _request('DELETE', f'/api/dibao_payment/{rid}')
            else:
                from data.excel_importer import delete_dibao_payment
                for rid in row_ids:
                    if rid:
                        delete_dibao_payment(rid)

            self._load_data()
            QMessageBox.information(self, "提示", "删除成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除失败：{e}")
