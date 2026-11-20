from .._imports import *
from .._consts import *
from ..funcs import *

UNDO_LIMIT = None

class ReportEditDialogLoadDataMixin:
    def _load_data(self, sheet=None):
        self._loading = True
        try:
            try:
                from network.client import _request
                path = f'/api/reports/{self.report_id}/data'
                if sheet:
                    from urllib.parse import quote
                    path += f'?sheet={quote(sheet)}'
                data = _request('GET', path)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"获取报表数据失败：{e}")
                self.reject()
                return
            headers = data.get('headers', []) or []
            rows = data.get('rows', []) or []
            if not headers:
                headers = [''] * max((len(r) for r in rows), default=0)
            self._suppress_change = True
            try:
                self._fill_table(headers, rows)
            finally:
                self._suppress_change = False
            # 工作表列表
            self._sheets = data.get('sheets', []) or []
            self._current_sheet = data.get('sheet_name', '') or (self._sheets[0] if self._sheets else '')
            self.combo_sheet.blockSignals(True)
            self.combo_sheet.clear()
            self.combo_sheet.addItems(self._sheets)
            if self._current_sheet in self._sheets:
                self.combo_sheet.setCurrentText(self._current_sheet)
            self.combo_sheet.setEnabled(len(self._sheets) > 1)
            self.combo_sheet.blockSignals(False)
            self._undo_stack.clear()
            self._redo_stack.clear()
            self._modified = False
            self.btn_save.setStyleSheet(
                f"background-color: {BTN_ADD_COLOR}; color: white; font-weight: bold; padding: 5px 18px;"
            )
            sheet_txt = f"工作表「{self._current_sheet}」" if self._current_sheet else ""
            self.lbl_status.setText(
                f"{sheet_txt} 已加载 {len(rows)} 行 × {len(headers)} 列（双击编辑；可增删行列/撤销重做/查找替换，完成后点保存）"
            )
        finally:
            self._loading = False
