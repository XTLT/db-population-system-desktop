import json
import urllib.request

from . import _base
from ._base import _get_ssl_context


def test_connection() -> bool:
    try:
        url = f"{_base.SERVER_URL}/api/health"
        ctx = _get_ssl_context() if _base.SERVER_URL.startswith('https') else None
        req = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data.get('healthy', False) or data.get('status') == 'ok'
    except Exception as e:
        print(f"连接测试失败: {e}")
        return False
