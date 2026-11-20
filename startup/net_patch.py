"""智能 IPv4/IPv6 选路补丁。

修复：域名同时有 A/AAAA 记录时，Windows 默认优先 IPv6，
而本机若 IPv6 路由不通会导致连接超时。
  - 本机与服务器同网段（内网）: IPv4 优先，秒连
  - 本机在外网（私网 IPv4 不可达）: IPv6 优先，走公网 IPv6
socket.create_connection 会遍历所有解析结果，排序即生效。

本模块 import 时即安装补丁（与原 main.py 的时机一致：在 PyQt6 / 业务模块
导入之前生效），并对外暴露 install_network_patch() 供显式调用。
"""

import socket as _socket

_orig_getaddrinfo = _socket.getaddrinfo


def _local_ipv4():
    """收集本机 IPv4 地址（gethostname + 出接口兜底）。"""
    ips = set()
    try:
        for r in _orig_getaddrinfo(_socket.gethostname(), None, _socket.AF_INET):
            ips.add(r[4][0])
    except Exception:
        pass
    try:
        s = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
        s.connect(("223.5.5.5", 80))
        ips.add(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    return ips


def _is_private_v4(ip):
    try:
        p = [int(x) for x in ip.split(".")]
        if len(p) != 4:
            return False
        a, b = p[0], p[1]
        return a == 10 or (a == 172 and 16 <= b <= 31) or (a == 192 and b == 168) or a == 127
    except Exception:
        return False


def _same_net24(a, b):
    pa, pb = a.split("."), b.split(".")
    return pa[:3] == pb[:3]


_LOCAL_IPV4 = _local_ipv4()


def _smart_getaddrinfo(host, port, family=0, *args, **kwargs):
    if family != _socket.AF_UNSPEC:
        return _orig_getaddrinfo(host, port, family, *args, **kwargs)
    results = _orig_getaddrinfo(host, port, _socket.AF_UNSPEC, *args, **kwargs)
    v4 = [r for r in results if r[0] == _socket.AF_INET]
    v6 = [r for r in results if r[0] == _socket.AF_INET6]
    if not v4 or not v6:
        return results
    if _LOCAL_IPV4:
        # 存在私网 IPv4 且本机不在其网段 → 该 IPv4 不可达 → IPv6 优先
        if any(_is_private_v4(r[4][0]) and not any(_same_net24(r[4][0], l) for l in _LOCAL_IPV4) for r in v4):
            return v6 + v4
    return v4 + v6


def install_network_patch():
    """把 socket.getaddrinfo 换成智能排序版本（幂等）。"""
    _socket.getaddrinfo = _smart_getaddrinfo


# import 时立即生效，保证早于所有网络客户端模块
install_network_patch()
