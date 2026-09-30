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
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        try:
            msg = json.loads(body).get('error', body)
        except Exception:
            msg = body
        if e.code == 401 and '/login' not in path and '/check_token' not in path and '/status' not in path and '/health' not in path:
            from ._relogin import _relogin
            _relogin()
            raise ConnectionError("登录已过期，请重新登录（登录框已自动弹出）")
        raise ConnectionError(f"服务器错误({e.code}): {msg}")
    except urllib.error.URLError as e:
        raise ConnectionError(f"请求失败: {url}\\n{e}")
