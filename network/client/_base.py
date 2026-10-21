import os
import ssl

SERVER_URL = ""
TOKEN = ""

# 证书固定：将服务端的 server.crt 放到此目录
# （包拆分后 __file__ 深了一层，多取一层 dirname 以保持解析结果仍为 desktop/certs）
_CERTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "certs",
)


def set_server_url(url: str):
    global SERVER_URL
    SERVER_URL = url.rstrip('/')


def get_server_url() -> str:
    return SERVER_URL


def set_token(token: str):
    global TOKEN
    TOKEN = token


def get_token() -> str:
    return TOKEN


def _get_ssl_context():
    """创建 SSL 上下文，支持证书固定验证 + mTLS 客户端证书

    安全方案：
    1. 如果 certs/server.crt 存在，使用该证书验证（推荐）
    2. 如果不存在，允许所有证书（开发/测试环境）
    3. 如果 certs/client.crt + client.key 存在，TLS 握手时出示客户端证书（mTLS 双向校验）

    部署时请将服务端的 server.crt 与客户端证书 client.crt/client.key 复制到 desktop/certs/ 目录
    """
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


def get_client_cert_args():
    """返回 requests 下载所需的 mTLS 客户端证书参数 (client.crt, client.key)。

    服务器（stunnel verify=2）要求客户端出示证书；下载更新包走服务器直连时
    必须带上，否则握手会被拒绝。证书缺失时返回 None（仅用于非服务器源）。
    """
    client_cert = os.path.join(_CERTS_DIR, "client.crt")
    client_key = os.path.join(_CERTS_DIR, "client.key")
    if os.path.exists(client_cert) and os.path.exists(client_key):
        return (client_cert, client_key)
    return None
