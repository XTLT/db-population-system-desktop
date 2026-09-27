import json
import urllib.request
import urllib.parse
import urllib.error

from . import _base
from ._base import _get_ssl_context


def api_delete_photo_on_server(person_id: str, photo_type: str = "身份证") -> dict:
    url = f"{_base.SERVER_URL}/api/person/{person_id}/photo?photo_type={urllib.parse.quote(photo_type)}"
    req = urllib.request.Request(url, method='DELETE')
    if _base.TOKEN:
        req.add_header('Authorization', f'Bearer {_base.TOKEN}')

    try:
        ctx = _get_ssl_context() if _base.SERVER_URL.startswith('https') else None
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.URLError as e:
        raise ConnectionError(f"删除服务器照片失败: {url}\n{e}")
