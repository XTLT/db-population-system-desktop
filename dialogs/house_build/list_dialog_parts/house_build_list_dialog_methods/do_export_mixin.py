from .._imports import *
from .._consts import *
from ..funcs import *

import os


class HouseBuildListDialogDoExportMixin:
    def _do_export(self, fmt):
        if not self.current_app_id:
            QMessageBox.information(self, "提示", "请先选择一条申请记录。")
            return
        row = self.table.currentRow()
        name = self.items[row].get('owner_name', '') if 0 <= row < len(self.items) else ''
        no = self.items[row].get('app_no', '') if 0 <= row < len(self.items) else ''
        suffix = 'xlsx' if fmt == 'xlsx' else 'pdf'
        default_name = '宅基地建房申请_%s_%s.%s' % (name or '未命名', no or '', suffix)
        path, _ = QFileDialog.getSaveFileName(
            self, "保存导出文件", default_name,
            'Excel 文件 (*.xlsx)' if fmt == 'xlsx' else 'PDF 文件 (*.pdf)',
        )
        if not path:
            return
        try:
            api_house_build_download(self.current_app_id, fmt, path)
        except Exception as e:
            QMessageBox.warning(self, "提示", f"导出失败：{e}")
            return
        if QMessageBox.question(
            self, "导出完成", "已保存到：\n%s\n\n现在打开吗？" % path,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        ) == QMessageBox.StandardButton.Yes:
            try:
                os.startfile(path)
            except Exception:
                pass
