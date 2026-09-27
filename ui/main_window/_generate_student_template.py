from PyQt6.QtWidgets import QFileDialog, QMessageBox


def _generate_student_template(self):
    from data.student_importer import export_student_education_template
    path, _ = QFileDialog.getSaveFileName(
        self, "保存模板", "学生就读信息模板.xlsx",
        "Excel文件 (*.xlsx)"
    )
    if path:
        export_student_education_template(path)
        QMessageBox.information(self, "成功", f"模板已生成：{path}")
