from PyQt6.QtWidgets import QFileDialog, QMessageBox


def _generate_forest_template(self):
    from data.excel_forest_template import generate_forest_template
    path, _ = QFileDialog.getSaveFileName(
        self, "保存模板", "林地面积导入模板.xlsx",
        "Excel文件 (*.xlsx)"
    )
    if path:
        generate_forest_template(path)
        QMessageBox.information(self, "成功", f"模板已生成：{path}")
