from .._imports import *
from .._consts import *
from ..funcs import *

LandSubsidyImportWorker = None

class LandSubsidyImportDialogOnErrorMixin:
    def _on_error(self, error_msg):
        self.lbl_status.setText("导入失败")
        QMessageBox.critical(self, "错误", f"导入失败：{error_msg}")
