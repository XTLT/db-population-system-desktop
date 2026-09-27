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
    """创建 SSL 上下文，支持证书固定验证

    安全方案：
    1. 如果 certs/server.crt 存在，使用该证书验证（推荐）
    2. 如果不存在，允许所有证书（开发/测试环境）

    部署时请将服务端的 server.crt 复制到 desktop/certs/ 目录
    """
    cert_file = os.path.join(_CERTS_DIR, "server.crt")

    if os.path.exists(cert_file):
        # 使用本地证书文件验证（证书固定）
        ctx = ssl.create_default_context()
        ctx.load_verify_locations(cert_file)
        ctx.check_hostname = False  # 自签名证书不验证 hostname
        ctx.verify_mode = ssl.CERT_REQUIRED
        return ctx
    else:
        # 未配置证书固定，允许所有证书（不安全）
        # 生产环境请将服务端证书复制到 certs/server.crt
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
