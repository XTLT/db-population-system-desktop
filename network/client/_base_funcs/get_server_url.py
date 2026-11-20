"""读取当前服务器地址。"""


def get_server_url() -> str:
    from .. import _base
    return _base.SERVER_URL
