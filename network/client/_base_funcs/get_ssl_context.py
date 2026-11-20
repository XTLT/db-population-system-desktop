"""创建 SSL 上下文，支持证书固定验证 + mTLS 客户端证书。

安全方案：
1. 如果 certs/server.crt 存在，使用该证书验证（推荐）
2. 如果不存在，允许所有证书（开发/测试环境）
3. 如果 certs/client.crt + client.key 存在，TLS 握手时出示客户端证书（mTLS 双向校验）

部署时请将服务端的 server.crt 与客户端证书 client.crt/client.key 复制到 desktop/certs/ 目录
"""

import os
import ssl


def get_ssl_context():
    from .._base import _CERTS_DIR

    cert_file = os.path.join(_CERTS_DIR, "server.crt")
    client_cert = os.path.join(_CERTS_DIR, "client.crt")
    client_key = os.path.join(_CERTS_DIR, "client.key")

    if os.path.exists(cert_file):
        # 使用本地证书文件验证（证书固定）
        ctx = ssl.create_default_context()
        ctx.load_verify_locations(cert_file)
        ctx.check_hostname = False  # 自签名证书不验证 hostname
        ctx.verify_mode = ssl.CERT_REQUIRED
    else:
        # 未配置证书固定，允许所有证书（不安全）
        # 生产环境请将服务端证书复制到 certs/server.crt
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    # mTLS：存在客户端证书则 TLS 握手时出示（服务器 verify=2 强制要求）
    if os.path.exists(client_cert) and os.path.exists(client_key):
        ctx.load_cert_chain(client_cert, client_key)
    return ctx
