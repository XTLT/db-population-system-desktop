from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogSaveMixin:
    def _save(self):
        headers, rows = self._collect_data()
        if not headers or all(h == '' for h in headers):
            QMessageBox.warning(self, "提示", "报表没有表头，无法保存")
            return
        self.btn_save.setEnabled(False)
        self.lbl_status.setText("正在保存...")
        try:
            from network.client import _request
            payload = {'headers': headers, 'rows': rows}
            if self._current_sheet:
                payload['sheet'] = self._current_sheet
            _request('POST', f'/api/reports/{self.report_id}/save', data=payload)
        except Exception as e:
            self.btn_save.setEnabled(True)
            self.lbl_status.setText("保存失败")
            QMessageBox.critical(self, "错误", f"保存失败：{e}")
            return
        self.btn_save.setEnabled(True)
        self.btn_save.setStyleSheet(
            f"background-color: {BTN_ADD_COLOR}; color: white; font-weight: bold; padding: 5px 18px;"
        )
        self._modified = False
        self.lbl_status.setText(f"保存成功（工作表「{self._current_sheet}」，{len(rows)} 行 × {len(headers)} 列）")
        QMessageBox.information(self, "提示", f"保存成功（工作表「{self._current_sheet}」，{len(rows)} 行 × {len(headers)} 列）")
