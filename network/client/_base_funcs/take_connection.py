"""从连接池取一个连接；空闲超时则丢弃重建。"""

import time

from .close_quietly import close_quietly
from .new_connection import new_connection


def take_connection(key, timeout):
    from .. import _base

    with _base._POOL_LOCK:
        entry = _base._CONN_POOL.pop(key, None)
    if entry is not None:
        conn, last_used = entry
        if time.monotonic() - last_used <= _base._IDLE_TTL:
            return conn, True
        close_quietly(conn)   # 空闲超时，服务端多半已关闭，直接丢弃重建
    return new_connection(key, timeout), False
