from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QProgressDialog
from data.excel_importer import backup_database


class _ManualBackupWorker(QThread):
    """在后台线程执行服务器备份请求，避免阻塞 GUI 线程导致界面假死、点击后无反应。"""

    success = pyqtSignal(object)  # 网络模式：返回服务器 result dict
    failure = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        try:
            from network.client import _request
            result = _request('POST', '/api/backup')
            self.success.emit(result)
        except Exception as e:
            self.failure.emit(str(e))


def _manual_backup(self):
    if self.is_network_mode:
        reply = QMessageBox.question(
            self, "确认备份",
            "确定要备份服务器数据库吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # 点击“是”后立即弹出模态不定态进度框，给出可见反馈并阻断主窗口操作；
        # 服务器端备份需复制数据库 + gzip 压缩全部照片 + 加密，3412 人数据可能耗时数秒到数十秒。
        # 原实现直接在 GUI 线程同步调用 _request，窗口会长时间假死、完成才弹结果框。
        progress = QProgressDialog("正在备份服务器数据，请稍候...", None, 0, 0, self)
        progress.setWindowTitle("备份中")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setCancelButton(None)
        progress.setMinimumDuration(0)
        progress.setRange(0, 0)  # 不定态（忙碌）进度条
        progress.show()

        worker = _ManualBackupWorker(parent=self)
        self._manual_backup_worker = worker  # 保持引用，避免被 GC 回收

        def _on_success(result):
            progress.close()
            if isinstance(result, dict) and result.get('success'):
                QMessageBox.information(self, "成功", "服务器数据库备份成功！")
            else:
                err = result.get('error', '未知错误') if isinstance(result, dict) else '未知错误'
                QMessageBox.critical(self, "备份失败", err)

        def _on_failure(msg):
            progress.close()
            QMessageBox.critical(self, "备份失败", msg)

        worker.success.connect(_on_success)
        worker.failure.connect(_on_failure)
        worker.start()
    else:
        path = backup_database()
        if path:
            QMessageBox.information(self, "成功", f"备份已保存到：{path}")
        else:
            QMessageBox.warning(self, "提示", "数据库文件不存在，无法备份")
