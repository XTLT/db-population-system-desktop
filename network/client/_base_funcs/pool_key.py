"""从 URL 提取连接池键 (scheme, host, port)。"""

from urllib.parse import urlsplit


def pool_key(url: str):
    parts = urlsplit(url)
    port = parts.port or (443 if parts.scheme == "https" else 80)
    return (parts.scheme, parts.hostname, port)
