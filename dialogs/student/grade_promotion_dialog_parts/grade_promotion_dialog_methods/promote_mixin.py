from .._imports import *
from .._consts import *
from ..funcs import *

GradePromotionWorker = None

class GradePromotionDialogPromoteMixin:
    def _promote(self):
        confirm_msg = "确定要执行升年级操作吗？"
        if not self.is_network:
            confirm_msg += "\n升年级前将自动备份数据库。"
        reply = QMessageBox.question(
            self, "确认升年级", confirm_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if not self.is_network:
                from data.excel_importer import backup_database
                backup_database()
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            self.worker = GradePromotionWorker(is_network=self.is_network)
            self.worker.finished.connect(self._on_finished)
            self.worker.error.connect(self._on_error)
            self.worker.start()
