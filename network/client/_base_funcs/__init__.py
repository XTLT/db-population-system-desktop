"""network.client._base 中各函数的统一调度出口。

私有函数沿用拆分前的下划线名，保证 `from ._base import _encode_path` 等
既有引用不需要改动。
"""

from .set_server_url import set_server_url
from .get_server_url import get_server_url
from .set_token import set_token
from .get_token import get_token
from .encode_path import encode_path as _encode_path
from .get_ssl_context import get_ssl_context as _get_ssl_context
from .get_client_cert_args import get_client_cert_args
from .get_ssl_context_cached import get_ssl_context_cached as _get_ssl_context_cached
from .pool_key import pool_key as _pool_key
from .new_connection import new_connection as _new_connection
from .take_connection import take_connection as _take_connection
from .release_connection import release_connection as _release_connection
from .close_quietly import close_quietly as _close_quietly
from .close_all_connections import close_all_connections
from .http_call import http_call

__all__ = [
    'set_server_url', 'get_server_url', 'set_token', 'get_token',
    '_encode_path', '_get_ssl_context', 'get_client_cert_args', '_get_ssl_context_cached',
    '_pool_key', '_new_connection', '_take_connection', '_release_connection', '_close_quietly',
    'close_all_connections', 'http_call',
]
