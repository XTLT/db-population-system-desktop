import os
import sys

VERSION_URLS = [
    "https://raw.githubusercontent.com/XTLT/db-population-system-desktop/master/updates/version.json",
]


def _get_config_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # 包拆分后 __file__ 深了一层，多取一层 dirname，使开发模式下
    # CONFIG_DIR 仍解析为原 network/ 目录（与原 update_checker.py 行为一致）。
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


CONFIG_DIR = _get_config_dir()
CONFIG_FILE = os.path.join(CONFIG_DIR, "version_config.json")
DOWNLOAD_DIR = os.path.join(CONFIG_DIR, "downloads")
