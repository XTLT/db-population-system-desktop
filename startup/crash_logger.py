"""兜底异常日志：未捕获异常写日志并弹框，避免 PyQt6 默认 qFatal 导致闪退。

PyQt6 在槽函数里遇到未捕获异常时，默认只走 sys.excepthook（默认实现会 abort
整个进程），用户看到的就只是"点了按钮程序没了"，没有任何痕迹。这里换成
自己实现的钩子：先落盘 traceback（含时间戳），再弹一个错误框，进程继续存活。
"""

import os
import sys


def install_crash_logger():
    import datetime
    import traceback
    from pathlib import Path

    from PyQt6.QtWidgets import QMessageBox

    base = Path(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")) / "人口通" / "logs"
    try:
        base.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    log_path = base / "crash.log"

    def _hook(exc_type, exc_value, exc_tb):
        text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(log_path, "a", encoding="utf-8") as fh:
                fh.write(f"\n[{stamp}] {exc_type.__name__}: {exc_value}\n{text}\n")
        except Exception:
            pass
        try:
            QMessageBox.critical(
                None, "程序错误",
                f"{exc_type.__name__}: {exc_value}\n\n详细信息已记录到：\n{log_path}",
            )
        except Exception:
            pass

    sys.excepthook = _hook
