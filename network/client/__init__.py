"""网络模式 HTTP 客户端（拆分后的同名包，行为与原 network/client.py 一致）。"""

from . import _base
from ._base import (
    set_server_url,
    get_server_url,
    set_token,
    get_token,
    _get_ssl_context,
    _CERTS_DIR,
)
from ._request import _request
from .api_login import api_login
from .api_search import api_search
from .api_persons_lookup_all import api_persons_lookup_all
from .api_family import api_family
from .api_person import api_person
from .api_add_person import api_add_person
from .api_update_education import api_update_education
from .api_deleted_persons import api_deleted_persons
from .api_recover_person import api_recover_person
from .api_students_search import api_students_search
from .api_new_hu_hao import api_new_hu_hao
from .api_add_household import api_add_household
from .api_update_person import api_update_person
from .api_delete_person import api_delete_person
from .api_migrate_person import api_migrate_person
from .api_students import api_students
from .api_stats import api_stats
from .api_promote_grades import api_promote_grades
from .api_upload_photo import api_upload_photo
from .api_download_photo import api_download_photo
from .api_delete_photo_on_server import api_delete_photo_on_server
from .api_export_filtered import api_export_filtered
from ._request_raw import _request_raw
from ._download_file import _download_file
from .test_connection import test_connection


def __getattr__(name):
    # SERVER_URL / TOKEN 是运行期可变全局，需通过属性访问实时读取，
    # 否则 `from network.client import TOKEN` 会拿到导入时的旧值。
    if name in ("SERVER_URL", "TOKEN"):
        return getattr(_base, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "SERVER_URL",
    "TOKEN",
    "_CERTS_DIR",
    "set_server_url",
    "get_server_url",
    "set_token",
    "get_token",
    "_get_ssl_context",
    "_request",
    "api_login",
    "api_search",
    "api_persons_lookup_all",
    "api_family",
    "api_person",
    "api_add_person",
    "api_update_education",
    "api_deleted_persons",
    "api_recover_person",
    "api_students_search",
    "api_new_hu_hao",
    "api_add_household",
    "api_update_person",
    "api_delete_person",
    "api_migrate_person",
    "api_students",
    "api_stats",
    "api_promote_grades",
    "api_upload_photo",
    "api_download_photo",
    "api_delete_photo_on_server",
    "api_export_filtered",
    "_request_raw",
    "_download_file",
    "test_connection",
]
