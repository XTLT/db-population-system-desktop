from .._imports import *
from .._consts import *
from ..funcs import *

import os

from dialogs.house_build.list_dialog_parts.house_build_list_dialog_methods.do_export_mixin import (
    _ask_meeting_info,
)


class HouseBuildEditDialogDoExportMixin:
    def _export_address(self):
        data = self.data or {}
        return (
            data.get('approval_address')
            or data.get('owner_hukou')
            or self.e_ap_address.text().strip()
            or self.e_owner_hukou.text().strip()
        )

    def _do_multi_export(self):
        parent = self.parent()
        handler = getattr(parent, '_do_batch_export', None)
        if not callable(handler):
            QMessageBox.information(
                self, "提示",
                "请关闭编辑窗口，回到宅基地建房列表，点“批量导出PDF”。",
            )
            return
        if QMessageBox.question(
            self, "多户导出",
            "批量导出使用服务器上已保存的数据。\n"
            "当前编辑内容如未保存，请先保存。\n\n现在打开多户勾选窗口吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        ) != QMessageBox.StandardButton.Yes:
            return
        handler(preselected_ids=[self.app_id] if self.app_id else None)

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

        meeting = None
        if fmt == 'pdf':
            meeting = _ask_meeting_info(self, address=self._export_address())
            if meeting is None:
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
            api_house_build_download(self.app_id, fmt, path, meeting=meeting)
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
