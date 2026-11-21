from .._imports import *
from .._consts import *
from ..funcs import *


class HouseBuildListDialogLoadDataMixin:
    def _load_data(self):
        if not self.is_network_mode:
            return
        keyword = self.txt_search.text().strip()
        year = self.txt_year.text().strip()
        status = self.cmb_status.currentData() or ''
        try:
            result = api_house_build_list(keyword=keyword, status=status, year=year, page=1, page_size=200)
        except Exception as e:
            QMessageBox.warning(self, "提示", f"查询失败：{e}")
            return

        self.items = result.get('items') or []
        self.table.setRowCount(len(self.items))
        for row, item in enumerate(self.items):
            values = [
                item.get('app_no', ''),
                item.get('owner_name', ''),
                item.get('owner_id_card', ''),
                item.get('hu_hao', ''),
                item.get('group_name', ''),
                fmt_area(item.get('apply_area_num')),
                STATUS_TEXT.get(item.get('status', ''), item.get('status', '')),
                item.get('created_at', ''),
            ]
            for col, text in enumerate(values):
                cell = QTableWidgetItem(str(text))
                if col in (5,):
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, col, cell)

        total = result.get('total', len(self.items))
        sum_area = fmt_area(result.get('sum_apply_area')) or '0'
        self.lbl_sum.setText('合计：%d 条，申请面积合计 %s ㎡' % (total, sum_area))
        self.current_app_id = None
        if self.items:
            self.table.selectRow(0)
            self.current_app_id = self.items[0].get('id')
