"""设置登录令牌。"""


def set_token(token: str):
    from .. import _base
    _base.TOKEN = token
