"""清空连接池（切换服务器地址、登出、程序退出时调用）。"""

from .close_quietly import close_quietly


def close_all_connections():
    from .. import _base

    with _base._POOL_LOCK:
        conns = list(_base._CONN_POOL.values())
        _base._CONN_POOL.clear()
    for entry in conns:
        close_quietly(entry[0] if isinstance(entry, tuple) else entry)
