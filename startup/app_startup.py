"""桌面端启动流程（QApplication 初始化、更新检查、进入事件循环）。"""

import sys
import signal

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont

from core.config import FONT_NAME, FONT_SIZE, ensure_dirs
from ui.main_window.workers import VersionCheckWorker

from .crash_logger import install_crash_logger
from .on_early_check import on_early_check
from .continue_startup import continue_startup


def main():
    ensure_dirs()
    from core.database import init_db
    init_db()

    app = QApplication(sys.argv)
    install_crash_logger()
    app.setFont(QFont(FONT_NAME, FONT_SIZE))
    app.setQuitOnLastWindowClosed(False)

    # Ctrl+C (SIGINT) 退出：事件循环运行期间收到中断信号时干净退出
    signal.signal(signal.SIGINT, lambda *a: QApplication.quit())
    # Qt C 事件循环期间外部 SIGINT 不会主动回到 Python 解释器，
    # 用低频定时器周期性回到 Python，使上面的 SIGINT 回调得以执行
    _sigint_wakeup = QTimer()
    _sigint_wakeup.start(200)
    _sigint_wakeup.timeout.connect(lambda: None)

    # ---- 启动第一时间检查更新（在连接/登录之前，后台线程）----
    window_ref = [None]
    early_check_done = [False]

    def _continue_startup():
        continue_startup(app, window_ref)

    early_worker = VersionCheckWorker()
    early_worker.finished.connect(
        lambda result, error: on_early_check(
            result, error, window_ref, early_check_done, _continue_startup
        )
    )
    early_worker.start()

    sys.exit(app.exec())
