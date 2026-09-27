from datetime import datetime
from PyQt6.QtWidgets import QFileDialog, QMessageBox


def _export_student_education(self):
    path, _ = QFileDialog.getSaveFileName(
        self, "导出就读信息", f"学生就读信息_{datetime.now().strftime('%Y%m%d')}.xlsx",
        "Excel文件 (*.xlsx)"
    )
    if not path:
        return
    if self.is_network_mode:
        try:
            from network.client import _download_file
            _download_file('/api/students/export', path)
            QMessageBox.information(self, "成功", f"数据已导出到：{path}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", str(e))
    else:
        from data.student_importer import export_student_education
        if export_student_education(path):
            QMessageBox.information(self, "成功", f"数据已导出到：{path}")
        else:
            QMessageBox.warning(self, "提示", "没有数据可导出")
