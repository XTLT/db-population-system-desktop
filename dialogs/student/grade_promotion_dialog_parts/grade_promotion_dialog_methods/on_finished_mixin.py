from .._imports import *
from .._consts import *
from ..funcs import *

GradePromotionWorker = None

class GradePromotionDialogOnFinishedMixin:
    def _on_finished(self, count):
        self.progress_bar.setVisible(False)
        QMessageBox.information(self, "完成", f"升年级完成！共升级 {count} 名学生。")
        self.accept()
