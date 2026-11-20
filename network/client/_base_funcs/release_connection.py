"""把连接放回池中；池满或同键已存在则关闭。"""

import time

from .close_quietly import close_quietly


def release_connection(key, conn):
    from .. import _base

    with _base._POOL_LOCK:
        if len(_base._CONN_POOL) >= _base._MAX_IDLE_CONNS or key in _base._CONN_POOL:
            close_quietly(conn)
            return
        _base._CONN_POOL[key] = (conn, time.monotonic())
