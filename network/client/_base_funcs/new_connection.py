"""按连接池键新建 HTTP(S) 连接。"""

import http.client

from .get_ssl_context_cached import get_ssl_context_cached


def new_connection(key, timeout):
    scheme, host, port = key
    if scheme == "https":
        return http.client.HTTPSConnection(host, port, context=get_ssl_context_cached(), timeout=timeout)
    return http.client.HTTPConnection(host, port, timeout=timeout)
