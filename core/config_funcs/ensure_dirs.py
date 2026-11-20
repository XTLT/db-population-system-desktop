"""启动时确保数据目录存在。"""

import os

from .paths import PHOTOS_DIR, BACKUP_DIR, LOG_DIR, CERT_DIR


def ensure_dirs():
    os.makedirs(PHOTOS_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(CERT_DIR, exist_ok=True)
