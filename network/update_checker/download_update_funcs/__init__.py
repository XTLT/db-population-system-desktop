"""下载更新包函数的统一调度出口。"""

from .sha256_file import sha256_file
from .download_update import download_update

__all__ = ['sha256_file', 'download_update']
