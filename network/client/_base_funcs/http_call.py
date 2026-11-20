"""用自己的连接池发一次 HTTP 请求，返回 (status, headers_list, body_bytes)。

复用语义：请求成功且服务端没要求关闭连接 → 连接放回池中，供下一次请求复用。
失效语义：复用来的连接已被服务端关闭（keepalive 到期）时，
  * 失败发生在"发送请求"阶段 → 请求肯定没送达，重建连接重试一次（任何方法都安全）；
  * 失败发生在"读取响应"阶段 → 请求可能已处理，只有幂等方法重试。
"""

import http.client
from urllib.parse import urlsplit

from .close_quietly import close_quietly
from .pool_key import pool_key
from .release_connection import release_connection
from .take_connection import take_connection

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


def http_call(method: str, url: str, body: bytes = None, headers: dict = None, timeout: int = 10):
    parts = urlsplit(url)
    target = parts.path or "/"
    if parts.query:
        target = target + "?" + parts.query

    key = pool_key(url)
    attempt = 0
    while True:
        conn, reused = take_connection(key, timeout)
        try:
            conn.timeout = timeout
        except Exception:
            pass

        try:
            conn.request(method, target, body=body, headers=headers or {})
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError,
                http.client.RemoteDisconnected) as exc:
            # 发送阶段就断了：请求没有送达服务端，重建后重试安全（含写操作）
            close_quietly(conn)
            if reused and attempt < 2:
                attempt += 1
                continue
            raise exc
        except Exception:
            close_quietly(conn)
            raise

        try:
            resp = conn.getresponse()
            data = resp.read()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError,
                http.client.RemoteDisconnected, http.client.IncompleteRead) as exc:
            # 响应阶段断：请求可能已被处理，只有幂等方法能重试
            close_quietly(conn)
            if method.upper() in SAFE_METHODS and attempt < 1:
                attempt += 1
                continue
            raise exc
        except Exception:
            close_quietly(conn)
            raise

        hdrs = resp.getheaders()
        keep = not resp.will_close
        if keep:
            release_connection(key, conn)
        else:
            close_quietly(conn)
        return resp.status, hdrs, data
