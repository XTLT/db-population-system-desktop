from .._imports import *
from .._consts import *
from ..funcs import *

DibaoImportWorker = None

class DibaoImportDialogStartImportMixin:
    def _start_import(self):
        if not self._file_path:
            QMessageBox.warning(self, "提示", "请先选择Excel文件！")
            return

        period = self.txt_period.text().strip()
        if not period:
            QMessageBox.warning(self, "提示", "请输入费款所属期（如202608）！")
            return

        self.lbl_status.setText("正在导入...")
        self._period = period
        self.lbl_status.setText("正在预检...")
        self.progress_bar.setValue(0)
        self._run_import(True)
