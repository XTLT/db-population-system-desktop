import json
import urllib.request
import urllib.error

from . import _base
from ._base import _get_ssl_context


def _request_raw(method: str, path: str, body: bytes, content_type: str) -> dict:
    url = f"{_base.SERVER_URL}{path}"
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header('Content-Type', content_type)
    if _base.TOKEN:
        req.add_header('Authorization', f'Bearer {_base.TOKEN}')
    try:
        ctx = _get_ssl_context() if _base.SERVER_URL.startswith('https') else None
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.URLError as e:
        raise ConnectionError(f"请求失败: {url}\n{e}")
