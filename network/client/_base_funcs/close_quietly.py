"""静默关闭连接，忽略关闭过程中的异常。"""


def close_quietly(conn):
    try:
        conn.close()
    except Exception:
        pass
