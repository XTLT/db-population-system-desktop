import http.client
import os
import ssl
import threading
import time
from urllib.parse import urlsplit

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
    new_url = url.rstrip('/')
    if new_url != SERVER_URL:
        # 服务器地址变了，旧连接池里的连接指向别的主机/证书，必须全部丢弃重建
        close_all_connections()
    SERVER_URL = new_url


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


# ---------------------------------------------------------------------------
# 连接复用（keep-alive）
#
# 背景：服务器 5000 端口是 gunicorn 自己终结 mTLS（--cert-reqs 2），在 ARM 单板上
# 一次完整双向握手约 105~122 ms，而业务处理只有 6 ms。桌面端原先每个请求都用
# urllib.request.urlopen 新建连接，于是"点一下按钮"要重付一次握手。
#
# 这里维护一个极简的 HTTPSConnection 池：连接建立后按 (scheme, host, port) 复用，
# 一个连接同一时刻只交给一个调用方。TLS 上下文仍用 _get_ssl_context()（证书固定 +
# mTLS 客户端证书），加密与认证强度与改造前完全一致，只是不再逐请求重握手。
#
# 安全约束（勿改）：
#   * 绝不跳过证书校验，始终用 _get_ssl_context() 建连接；
#   * 地址变化（set_server_url）必须清空池，防止请求发往旧主机；
#   * 连接失效时只在"请求尚未送达"的情况下重建重试，写操作不得盲目重发。
# ---------------------------------------------------------------------------

_POOL_LOCK = threading.Lock()
_CONN_POOL = {}
_MAX_IDLE_CONNS = 6

# 连接空闲多少秒后主动丢弃。
# 服务器 gunicorn 已设置 --keep-alive 65（2026-11-07 在 50 实测：空闲 40 秒仍可复用，70 秒失效）。
# 若客户端拿着已被服务端关掉的连接发请求，会先失败一次再重建重试，反而多一次往返。
# 这里取 60 秒，比服务端小 5 秒留余量，避开服务端关闭的临界点，保证不会用到死连接。
# 若日后调整服务端 --keep-alive，这里必须同步调整（保持比服务端小 5 秒左右）。
_IDLE_TTL = 60

_CTX_CACHE = {}
_CTX_LOCK = threading.Lock()


def _get_ssl_context_cached():
    """缓存 SSLContext，避免每次新建连接都重新读取证书文件。证书文件变化（mtime 变）自动重建。"""
    cert_file = os.path.join(_CERTS_DIR, "server.crt")
    client_cert = os.path.join(_CERTS_DIR, "client.crt")
    client_key = os.path.join(_CERTS_DIR, "client.key")
    try:
        key = (
            cert_file,
            os.path.getmtime(cert_file) if os.path.exists(cert_file) else 0,
            os.path.getmtime(client_cert) if os.path.exists(client_cert) else 0,
            os.path.getmtime(client_key) if os.path.exists(client_key) else 0,
        )
    except OSError:
        return _get_ssl_context()
    with _CTX_LOCK:
        ctx = _CTX_CACHE.get(key)
        if ctx is None:
            ctx = _get_ssl_context()
            _CTX_CACHE.clear()
            _CTX_CACHE[key] = ctx
    return ctx


def _pool_key(url: str):
    parts = urlsplit(url)
    port = parts.port or (443 if parts.scheme == "https" else 80)
    return (parts.scheme, parts.hostname, port)


def _new_connection(key, timeout):
    scheme, host, port = key
    if scheme == "https":
        return http.client.HTTPSConnection(host, port, context=_get_ssl_context_cached(), timeout=timeout)
    return http.client.HTTPConnection(host, port, timeout=timeout)


def _take_connection(key, timeout):
    with _POOL_LOCK:
        entry = _CONN_POOL.pop(key, None)
    if entry is not None:
        conn, last_used = entry
        if time.monotonic() - last_used <= _IDLE_TTL:
            return conn, True
        _close_quietly(conn)   # 空闲超时，服务端多半已关闭，直接丢弃重建
    return _new_connection(key, timeout), False


def _release_connection(key, conn):
    with _POOL_LOCK:
        if len(_CONN_POOL) >= _MAX_IDLE_CONNS or key in _CONN_POOL:
            _close_quietly(conn)
            return
        _CONN_POOL[key] = (conn, time.monotonic())


def _close_quietly(conn):
    try:
        conn.close()
    except Exception:
        pass


def close_all_connections():
    """清空连接池（切换服务器地址、登出、程序退出时调用）。"""
    with _POOL_LOCK:
        conns = list(_CONN_POOL.values())
        _CONN_POOL.clear()
    for entry in conns:
        _close_quietly(entry[0] if isinstance(entry, tuple) else entry)


_SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


def http_call(method: str, url: str, body: bytes = None, headers: dict = None, timeout: int = 10):
    """用自己的连接池发一次 HTTP 请求，返回 (status, headers_list, body_bytes)。

    复用语义：请求成功且服务端没要求关闭连接 → 连接放回池中，供下一次请求复用。
    失效语义：复用来的连接已被服务端关闭（keepalive 到期）时，
      * 失败发生在"发送请求"阶段 → 请求肯定没送达，重建连接重试一次（任何方法都安全）；
      * 失败发生在"读取响应"阶段 → 请求可能已处理，只有幂等方法重试。
    """
    parts = urlsplit(url)
    target = parts.path or "/"
    if parts.query:
        target = target + "?" + parts.query

    key = _pool_key(url)
    attempt = 0
    while True:
        conn, reused = _take_connection(key, timeout)
        try:
            conn.timeout = timeout
        except Exception:
            pass

        try:
            conn.request(method, target, body=body, headers=headers or {})
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError,
                http.client.RemoteDisconnected) as exc:
            # 发送阶段就断了：请求没有送达服务端，重建后重试安全（含写操作）
            _close_quietly(conn)
            if reused and attempt < 2:
                attempt += 1
                continue
            raise exc
        except Exception:
            _close_quietly(conn)
            raise

        try:
            resp = conn.getresponse()
            data = resp.read()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError,
                http.client.RemoteDisconnected, http.client.IncompleteRead) as exc:
            # 响应阶段断：请求可能已被处理，只有幂等方法能重试
            _close_quietly(conn)
            if method.upper() in _SAFE_METHODS and attempt < 1:
                attempt += 1
                continue
            raise exc
        except Exception:
            _close_quietly(conn)
            raise

        hdrs = resp.getheaders()
        keep = not resp.will_close
        if keep:
            _release_connection(key, conn)
        else:
            _close_quietly(conn)
        return resp.status, hdrs, data

