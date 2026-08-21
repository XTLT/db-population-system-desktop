from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR
from network.client import get_server_url


class GradePromotionWorker(QThread):
    finished = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, is_network=False):
        super().__init__()
        self.is_network = is_network

    def run(self):
        try:
            if self.is_network:
                from network.client import api_promote_grades
                result = api_promote_grades()
                if result.get('success'):
                    self.finished.emit(result.get('count', 0))
                else:
                    self.error.emit(result.get('error', '升级失败'))
            else:
                from core.database import promote_all_grades
                count = promote_all_grades()
                self.finished.emit(count)
        except Exception as e:
            self.error.emit(str(e))


class GradePromotionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("年级升级")
        self.setFixedSize(400, 200)
        self.worker = None
        self.is_network = bool(get_server_url())
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("每年9月1日自动升年级")
        title.setFont(QFont(FONT_NAME, 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        mode_text = "（网络模式：服务器端执行）" if self.is_network else ""
        info = QLabel(
            f"将为所有在读学生自动升入下一个年级{mode_text}\n"
            "特殊升学：K3→G1、G9→G10、G12→U1、Z3→U3\n"
            "V3/J3/C3/Z3/U5/M3/D4 升级后标记为毕业\n"
            "标记为留级/休学/转学的学生不升年级"
        )
        info.setFont(QFont(FONT_NAME, FONT_SIZE))
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        btn_layout = QHBoxLayout()
        btn_promote = QPushButton("开始升年级")
        btn_promote.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 10px;")
        btn_promote.clicked.connect(self._promote)
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 10px;")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_promote)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

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

    def _on_finished(self, count):
        self.progress_bar.setVisible(False)
        QMessageBox.information(self, "完成", f"升年级完成！共升级 {count} 名学生。")
        self.accept()

    def _on_error(self, error_msg):
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "错误", f"升年级失败：{error_msg}")
