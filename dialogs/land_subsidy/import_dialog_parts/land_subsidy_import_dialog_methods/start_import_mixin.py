from .._imports import *
from .._consts import *
from ..funcs import *

LandSubsidyImportWorker = None

class LandSubsidyImportDialogStartImportMixin:
    def _start_import(self):
        if not self._file_path:
            QMessageBox.warning(self, "提示", "请先选择Excel文件！")
            return

        year = self.txt_year_input.text().strip()
        if not year:
            year = str(datetime.now().year)

        self.lbl_status.setText("正在导入...")
        self._year = year
        self.lbl_status.setText("正在预检...")
        self.progress_bar.setValue(0)
        self._run_import(True)
