from .._imports import *
from .._consts import *
from ..funcs import *

ImportWorker = None

class ImportDialogBrowseMixin:
    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "",
            "Excel文件 (*.xlsx *.xls)"
        )
        if path:
            self._file_path = path
            self.lbl_file.setText(path)
