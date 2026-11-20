from .._imports import *
from .._consts import *
from ..funcs import *

GradePromotionWorker = None

class GradePromotionDialogOnErrorMixin:
    def _on_error(self, error_msg):
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "错误", f"升年级失败：{error_msg}")
