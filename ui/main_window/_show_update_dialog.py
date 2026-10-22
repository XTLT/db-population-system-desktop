from PyQt6.QtWidgets import QVBoxLayout, QTextEdit, QHBoxLayout, QDialog, QLabel, QProgressBar, QPushButton, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.config import FONT_NAME
from .workers import VersionCheckWorker


def _show_update_dialog(self, version_info):
                 

    if getattr(self, '_update_dialog', None):
        self._update_dialog.raise_()
        self._update_dialog.activateWindow()
        return

    # 一律独立顶层窗口（不挂 parent），避免被连接/登录窗口的
    # 应用级模态禁用输入导致"立即更新"点不动。
    parent = None
    self._update_dialog = QDialog(parent)
    self._update_dialog.setWindowTitle("检查更新")
    self._update_dialog.setFixedSize(480, 320)
    self._update_dialog.setModal(False)
    flags = self._update_dialog.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
    # 启动阶段登录窗口可能已先显示为模态，更新窗口必须置顶才能被点按
    flags |= Qt.WindowType.WindowStaysOnTopHint
    flags |= Qt.WindowType.Dialog
    self._update_dialog.setWindowFlags(flags)
    self._update_btn_now = None
    self._update_dialog.finished.connect(lambda: (setattr(self, '_update_dialog', None), setattr(self, '_update_btn_now', None)))
    layout = QVBoxLayout(self._update_dialog)
    layout.setSpacing(12)

    self._update_status = QLabel("正在检查更新...")
    self._update_status.setFont(QFont(FONT_NAME, 11))
    self._update_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(self._update_status)

    self._update_progress = QProgressBar()
    self._update_progress.setRange(0, 0)
    layout.addWidget(self._update_progress)

    self._update_info = QTextEdit()
    self._update_info.setReadOnly(True)
    self._update_info.setMaximumHeight(120)
    self._update_info.setVisible(False)
    layout.addWidget(self._update_info)

    btn_layout = QHBoxLayout()
    self._update_btn_close = QPushButton("关闭")
    # 用 reject 而非 close：reject -> done -> finished 信号必发，
    # 保证"暂不更新"一定能驱动启动流程继续（close 在个别环境可能不触发 finished）
    self._update_btn_close.clicked.connect(self._update_dialog.reject)
    self._update_btn_close.setVisible(False)
    btn_layout.addStretch()
    btn_layout.addWidget(self._update_btn_close)
    layout.addLayout(btn_layout)

    self._update_dialog.show()
    self._update_dialog.raise_()
    self._update_dialog.activateWindow()

    if version_info:
        self._on_version_check_done(version_info, "")
    else:
        self._version_worker = VersionCheckWorker()
        self._version_worker.finished.connect(self._on_version_check_done)
        self._version_worker.start()
