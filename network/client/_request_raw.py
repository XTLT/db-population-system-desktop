import json

from . import _base


def _request_raw(method: str, path: str, body: bytes, content_type: str) -> dict:
    url = f"{_base.SERVER_URL}{path}"
    headers = {'Content-Type': content_type}
    if _base.TOKEN:
        headers['Authorization'] = f'Bearer {_base.TOKEN}'

    try:
        # 走连接池：与 _request 共用同一条复用连接
        status, _headers, raw = _base.http_call(method, url, body, headers, timeout=30)
    except Exception as e:
        raise ConnectionError(f"请求失败: {url}\n{e}")

    if 200 <= status < 300:
        return json.loads(raw.decode('utf-8'))

    body_text = raw.decode('utf-8', errors='replace')
    try:
        msg = json.loads(body_text).get('error', body_text)
    except Exception:
        msg = body_text
    if status == 401 and '/login' not in path and '/check_token' not in path and '/status' not in path and '/health' not in path:
        from ._relogin import _relogin
        _relogin()
        raise ConnectionError("登录已过期，请重新登录（登录框已自动弹出）")
    raise ConnectionError(f"服务器错误({status}): {msg}")
