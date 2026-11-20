"""读取当前登录令牌。"""


def get_token() -> str:
    from .. import _base
    return _base.TOKEN
