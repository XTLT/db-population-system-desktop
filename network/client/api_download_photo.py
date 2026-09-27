import shutil
import urllib.request
import urllib.error

from . import _base
from ._base import _get_ssl_context


def api_download_photo(person_id: str, save_path: str) -> bool:
    url = f"{_base.SERVER_URL}/api/person/{person_id}/photo"
    req = urllib.request.Request(url, method='GET')
    if _base.TOKEN:
        req.add_header('Authorization', f'Bearer {_base.TOKEN}')

    try:
        ctx = _get_ssl_context() if _base.SERVER_URL.startswith('https') else None
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            with open(save_path, 'wb') as f:
                shutil.copyfileobj(resp, f)
            return True
    except urllib.error.URLError as e:
        raise ConnectionError(f"下载照片失败: {url}\n{e}")
