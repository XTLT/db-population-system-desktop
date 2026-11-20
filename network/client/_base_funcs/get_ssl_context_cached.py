"""缓存 SSLContext，避免每次新建连接都重新读取证书文件。证书文件变化（mtime 变）自动重建。"""

import os

from .get_ssl_context import get_ssl_context


def get_ssl_context_cached():
    from .. import _base

    cert_file = os.path.join(_base._CERTS_DIR, "server.crt")
    client_cert = os.path.join(_base._CERTS_DIR, "client.crt")
    client_key = os.path.join(_base._CERTS_DIR, "client.key")
    try:
        key = (
            cert_file,
            os.path.getmtime(cert_file) if os.path.exists(cert_file) else 0,
            os.path.getmtime(client_cert) if os.path.exists(client_cert) else 0,
            os.path.getmtime(client_key) if os.path.exists(client_key) else 0,
        )
    except OSError:
        return get_ssl_context()
    with _base._CTX_LOCK:
        ctx = _base._CTX_CACHE.get(key)
        if ctx is None:
            ctx = get_ssl_context()
            _base._CTX_CACHE.clear()
            _base._CTX_CACHE[key] = ctx
    return ctx
