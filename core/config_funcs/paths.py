"""数据与资源目录常量。

注意：BASE_DIR 的取值与原 core/config.py 中的 `dirname(__file__)` 等价，
本文件位于 core/config_funcs/，因此需要多退一层。
"""

import os
import sys

APP_NAME = "人口通"

# 原 core/config.py 中 BASE_DIR = dirname(abspath(__file__))（即 core 目录）；
# 本文件在 core/config_funcs/ 下，因此多退一层。
_BASE_OVERRIDE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = _BASE_OVERRIDE

# 原 core/config.py 用于定位 updates/version.json 的目录（三层 dirname = split 层）；
# 本文件多退一层后共四层，保持与拆分前完全一致。
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


if sys.platform == "win32":
    APPDATA_DIR = os.path.join(os.environ.get("APPDATA", BASE_DIR), APP_NAME)
else:
    APPDATA_DIR = os.path.join(os.path.expanduser("~"), ".config", APP_NAME)

_OLD_APP_NAME = "人口信息查询系统"
if sys.platform == "win32":
    _OLD_APPDATA_DIR = os.path.join(os.environ.get("APPDATA", BASE_DIR), _OLD_APP_NAME)
else:
    _OLD_APPDATA_DIR = os.path.join(os.path.expanduser("~"), ".config", _OLD_APP_NAME)


DB_PATH = os.path.join(BASE_DIR, "population.db")
PHOTOS_DIR = os.path.join(BASE_DIR, "Photos")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
LOG_DIR = os.path.join(BASE_DIR, "logs")
CERT_DIR = os.path.join(BASE_DIR, "certs")
