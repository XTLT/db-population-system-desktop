"""返回 requests 下载所需的 mTLS 客户端证书参数 (client.crt, client.key)。

服务器（stunnel verify=2）要求客户端出示证书；下载更新包走服务器直连时
必须带上，否则握手会被拒绝。证书缺失时返回 None（仅用于非服务器源）。
"""

import os


def get_client_cert_args():
    from .._base import _CERTS_DIR

    client_cert = os.path.join(_CERTS_DIR, "client.crt")
    client_key = os.path.join(_CERTS_DIR, "client.key")
    if os.path.exists(client_cert) and os.path.exists(client_key):
        return (client_cert, client_key)
    return None
