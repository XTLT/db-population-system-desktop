import json
import urllib.request
import urllib.error

from . import _base
from ._base import _get_ssl_context


def api_export_filtered(save_path: str, filters: dict = None, password: str = ""):
    url = f"{_base.SERVER_URL}/api/export/excel"
    data = {'password': password}
    if filters:
        data['filters'] = filters
    req_data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=req_data, method='POST')
    req.add_header('Content-Type', 'application/json')
    if _base.TOKEN:
        req.add_header('Authorization', f'Bearer {_base.TOKEN}')

    ctx = _get_ssl_context() if _base.SERVER_URL.startswith('https') else None
    try:
        with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
            with open(save_path, 'wb') as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        try:
            msg = json.loads(body).get('error', body)
        except Exception:
            msg = body
        raise ConnectionError(f"导出失败({e.code}): {msg}")
