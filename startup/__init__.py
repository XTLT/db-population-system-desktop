"""桌面端启动阶段的函数集合（网络补丁、崩溃日志、更新检查分支、登录与主窗口）。
"""

from .net_patch import install_network_patch  # noqa: F401  （import 即安装补丁）
from .crash_logger import install_crash_logger
from .on_early_check import on_early_check
from .continue_startup import continue_startup

__all__ = ['install_network_patch', 'install_crash_logger', 'on_early_check', 'continue_startup']
