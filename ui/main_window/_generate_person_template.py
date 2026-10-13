from PyQt6.QtWidgets import QFileDialog, QMessageBox


def _generate_person_template(self):
    from data.excel_importer.generate_template import generate_template
    path, _ = QFileDialog.getSaveFileName(
        self, "保存模板", "人口信息导入模板.xlsx",
        "Excel文件 (*.xlsx)"
    )
    if path:
        generate_template(path)
        QMessageBox.information(self, "成功", f"模板已生成：{path}")
