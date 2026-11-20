"""config 函数的统一调度出口。"""

from .paths import (
    APP_NAME,
    BASE_DIR,
    PROJECT_ROOT,
    APPDATA_DIR,
    DB_PATH,
    PHOTOS_DIR,
    BACKUP_DIR,
    LOG_DIR,
    CERT_DIR,
    _OLD_APP_NAME,
    _OLD_APPDATA_DIR,
)
from .migrate_old_appdata import migrate_old_appdata
from .load_app_version import load_app_version
from .ensure_dirs import ensure_dirs

__all__ = [
    'APP_NAME', 'BASE_DIR', 'PROJECT_ROOT', 'APPDATA_DIR',
    'DB_PATH', 'PHOTOS_DIR', 'BACKUP_DIR', 'LOG_DIR', 'CERT_DIR',
    'migrate_old_appdata', 'load_app_version', 'ensure_dirs',
]
