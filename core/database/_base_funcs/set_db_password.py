"""设置数据库密码（同时尽力写入系统密钥环）。"""


def set_db_password(password: str):
    from .. import _base

    _base._db_password = password
    try:
        import keyring
        keyring.set_password(_base.SERVICE_NAME, "db_password", password)
    except Exception:
        pass
