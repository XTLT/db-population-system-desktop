"""更新检查（拆分后的同名包，行为与原 network/update_checker.py 一致）。"""

from ._base import (
    VERSION_URLS,
    _get_config_dir,
    CONFIG_DIR,
    CONFIG_FILE,
    DOWNLOAD_DIR,
)
from .load_local_config import load_local_config
from .save_local_config import save_local_config
from ._get_server_url_and_token import _get_server_url_and_token
from ._check_local_server import _check_local_server
from .check_update import check_update
from ._get_release_download_url import _get_release_download_url
from .download_update import download_update
from .calculate_sha256 import calculate_sha256
from .verify_file import verify_file
from .update_local_version import update_local_version
from .apply_update import apply_update

__all__ = [
    "VERSION_URLS",
    "_get_config_dir",
    "CONFIG_DIR",
    "CONFIG_FILE",
    "DOWNLOAD_DIR",
    "load_local_config",
    "save_local_config",
    "_get_server_url_and_token",
    "_check_local_server",
    "check_update",
    "_get_release_download_url",
    "download_update",
    "calculate_sha256",
    "verify_file",
    "update_local_version",
    "apply_update",
]
