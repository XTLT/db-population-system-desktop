import urllib.request
import urllib.error

from . import _base
from ._base import _get_ssl_context


def _download_file(path: str, save_path: str):
    url = f"{_base.SERVER_URL}{path}"
    req = urllib.request.Request(url, method='GET')
    if _base.TOKEN:
        req.add_header('Authorization', f'Bearer {_base.TOKEN}')
    try:
        ctx = _get_ssl_context() if _base.SERVER_URL.startswith('https') else None
        with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
            with open(save_path, 'wb') as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
    except urllib.error.URLError as e:
        raise ConnectionError(f"下载失败: {url}\n{e}")
