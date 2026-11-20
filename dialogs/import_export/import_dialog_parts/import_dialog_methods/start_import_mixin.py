from .._imports import *
from .._consts import *
from ..funcs import *

ImportWorker = None

class ImportDialogStartImportMixin:
    def _start_import(self):
        if not self._file_path:
            QMessageBox.warning(self, "提示", "请先选择Excel文件！")
            return
        mode = "full" if self.radio_full.isChecked() else "incremental"
        if mode == "full":
            reply = QMessageBox.question(
                self, "全量导入确认",
                "将清空现有全部人员数据，确定？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                self.lbl_status.setText("已取消全量导入")
                return
        self.lbl_status.setText("正在导入...")
        self.progress_bar.setValue(0)
        self.worker = ImportWorker(self._file_path, mode)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()
