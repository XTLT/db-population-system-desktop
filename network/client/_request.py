import json

from . import _base


def _request(method: str, path: str, data: dict = None) -> dict:
    url = f"{_base.SERVER_URL}{path}"
    body = None
    headers = {}
    if data:
        body = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    if _base.TOKEN:
        headers['Authorization'] = f'Bearer {_base.TOKEN}'

    try:
        # 走连接池：同一台服务器的连续请求复用同一条 mTLS 连接，不再逐请求重握手
        status, _headers, raw = _base.http_call(method, url, body, headers, timeout=10)
    except Exception as e:
        raise ConnectionError(f"无法连接服务器: {url}\n{e}")

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
