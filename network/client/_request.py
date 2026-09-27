import json
import urllib.request
import urllib.error

from . import _base
from ._base import _get_ssl_context


def _request(method: str, path: str, data: dict = None) -> dict:
    url = f"{_base.SERVER_URL}{path}"
    if data:
        req_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=req_data, method=method)
        req.add_header('Content-Type', 'application/json')
    else:
        req = urllib.request.Request(url, method=method)

    if _base.TOKEN:
        req.add_header('Authorization', f'Bearer {_base.TOKEN}')

    try:
        ctx = _get_ssl_context() if _base.SERVER_URL.startswith('https') else None
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        try:
            msg = json.loads(body).get('error', body)
        except Exception:
            msg = body
        raise ConnectionError(f"服务器错误({e.code}): {msg}")
    except urllib.error.URLError as e:
        raise ConnectionError(f"无法连接服务器: {url}\n{e}")
