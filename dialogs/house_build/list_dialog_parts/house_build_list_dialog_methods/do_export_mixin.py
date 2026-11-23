from .._imports import *
from .._consts import *
from ..funcs import *

import os


class HouseBuildListDialogDoExportMixin:
    def _selected_rows(self):
        model = self.table.selectionModel()
        if model is None:
            return []
        return sorted({index.row() for index in model.selectedRows()})

    def _do_batch_export(self):
        rows = [row for row in self._selected_rows() if 0 <= row < len(self.items)]
        if len(rows) < 2:
            QMessageBox.information(
                self, "提示",
                "请按 Ctrl/Shift 至少选择两户。\n单户导出请点“导出PDF”。",
            )
            return
        if len(rows) > 50:
            QMessageBox.information(self, "提示", "一次最多导出 50 户。")
            return

        app_ids = [self.items[row].get('id') for row in rows if self.items[row].get('id')]
        if len(app_ids) != len(rows):
            QMessageBox.warning(self, "提示", "选中的记录缺少申请 ID，请刷新后重试。")
            return

        default_name = '宅基地建房一户一档_%d户.pdf' % len(app_ids)
        path, _ = QFileDialog.getSaveFileName(
            self, "批量导出（多户合并）", default_name, 'PDF 文件 (*.pdf)',
        )
        if not path:
            return
        try:
            api_house_build_batch_download(app_ids, path)
        except Exception as e:
            QMessageBox.warning(self, "提示", f"批量导出失败：{e}")
            return
        if QMessageBox.question(
            self, "导出完成",
            "已将 %d 户合并为一个 PDF：\n每户 6 页（申请表、审批表、4 张一户表），"
            "最后共用 1 张会议记录和 1 张公示。\n\n已保存到：\n%s\n\n现在打开吗？"
            % (len(app_ids), path),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        ) == QMessageBox.StandardButton.Yes:
            try:
                os.startfile(path)
            except Exception:
                pass

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
