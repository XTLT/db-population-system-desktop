"""设置服务器地址；地址变化时清空连接池。"""


def set_server_url(url: str):
    from .. import _base

    new_url = url.rstrip('/')
    if new_url != _base.SERVER_URL:
        # 服务器地址变了，旧连接池里的连接指向别的主机/证书，必须全部丢弃重建
        _base.close_all_connections()
    _base.SERVER_URL = new_url
