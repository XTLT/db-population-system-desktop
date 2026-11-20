"""网络客户端共享状态 + 函数出口。

模块级状态（SERVER_URL / TOKEN / 连接池 / 证书上下文缓存）保留在本模块，
因为 client 包内多个模块直接读取 `_base.SERVER_URL`、`_base.TOKEN`。
各函数实现已拆到 _base_funcs/，函数内部通过 `from .. import _base`
读写这里的同一份状态，不存在多份副本。

--------------------------------------------------------------------------------
连接复用（keep-alive）

背景：服务器 5000 端口是 gunicorn 自己终结 mTLS（--cert-reqs 2），在 ARM 单板上
一次完整双向握手约 105~122 ms，而业务处理只有 6 ms。桌面端原先每个请求都用
urllib.request.urlopen 新建连接，于是"点一下按钮"要重付一次握手。

这里维护一个极简的 HTTPSConnection 池：连接建立后按 (scheme, host, port) 复用，
一个连接同一时刻只交给一个调用方。TLS 上下文仍用 _get_ssl_context()（证书固定 +
mTLS 客户端证书），加密与认证强度与改造前完全一致，只是不再逐请求重握手。

安全约束（勿改）：
  * 绝不跳过证书校验，始终用 _get_ssl_context() 建连接；
  * 地址变化（set_server_url）必须清空池，防止请求发往旧主机；
  * 连接失效时只在"请求尚未送达"的情况下重建重试，写操作不得盲目重发。
--------------------------------------------------------------------------------
"""

import os
import threading

SERVER_URL = ""
TOKEN = ""

# 证书固定：将服务端的 server.crt 放到此目录
# （包拆分后 __file__ 深了一层，多取一层 dirname 以保持解析结果仍为 desktop/certs）
_CERTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "certs",
)

# 连接池状态
_POOL_LOCK = threading.Lock()
_CONN_POOL = {}
_MAX_IDLE_CONNS = 6

# 连接空闲多少秒后主动丢弃。
# 服务器 gunicorn 已设置 --keep-alive 65（2026-11-07 在 50 实测：空闲 40 秒仍可复用，70 秒失效）。
# 若客户端拿着已被服务端关掉的连接发请求，会先失败一次再重建重试，反而多一次往返。
# 这里取 60 秒，比服务端小 5 秒留余量，避开服务端关闭的临界点，保证不会用到死连接。
# 若日后调整服务端 --keep-alive，这里必须同步调整（保持比服务端小 5 秒左右）。
_IDLE_TTL = 60

# SSLContext 缓存
_CTX_CACHE = {}
_CTX_LOCK = threading.Lock()

# 幂等方法（响应阶段断线时可安全重试）
_SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


from ._base_funcs import (  # noqa: E402,F401
    set_server_url,
    get_server_url,
    set_token,
    get_token,
    _encode_path,
    _get_ssl_context,
    get_client_cert_args,
    _get_ssl_context_cached,
    _pool_key,
    _new_connection,
    _take_connection,
    _release_connection,
    _close_quietly,
    close_all_connections,
    http_call,
)

__all__ = [
    'SERVER_URL', 'TOKEN',
    'set_server_url', 'get_server_url', 'set_token', 'get_token',
    '_encode_path', '_get_ssl_context', 'get_client_cert_args', '_get_ssl_context_cached',
    '_pool_key', '_new_connection', '_take_connection', '_release_connection', '_close_quietly',
    'close_all_connections', 'http_call',
]
