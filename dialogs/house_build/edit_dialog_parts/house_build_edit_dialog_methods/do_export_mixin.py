from .._imports import *
from .._consts import *
from ..funcs import *

import os


class HouseBuildEditDialogDoExportMixin:
    def _do_export(self, fmt):
        if not self.app_id:
            QMessageBox.information(self, "提示", "请先保存，再导出打印文件。")
            return
        if QMessageBox.question(
            self, "导出前确认",
            "导出内容取自服务器上已保存的数据。\n如刚修改过还没保存，请先保存。\n\n现在导出吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        ) != QMessageBox.StandardButton.Yes:
            return

        name = (self.data or {}).get('owner_name', '') or self.e_owner_name.text().strip()
        no = self.txt_app_no.text().strip()
        suffix = 'xlsx' if fmt == 'xlsx' else 'pdf'
        default_name = '宅基地建房申请_%s_%s.%s' % (name or '未命名', no or '', suffix)
        path, _ = QFileDialog.getSaveFileName(
            self, "保存导出文件", default_name,
            'Excel 文件 (*.xlsx)' if fmt == 'xlsx' else 'PDF 文件 (*.pdf)',
        )
        if not path:
            return
        try:
            api_house_build_download(self.app_id, fmt, path)
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
