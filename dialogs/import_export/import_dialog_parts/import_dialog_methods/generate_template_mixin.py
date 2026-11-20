from .._imports import *
from .._consts import *
from ..funcs import *

ImportWorker = None

class ImportDialogGenerateTemplateMixin:
    def _generate_template(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "保存模板", "人口信息导入模板.xlsx",
            "Excel文件 (*.xlsx)"
        )
        if path:
            generate_template(path)
            QMessageBox.information(self, "成功", f"模板已生成：{path}")
