import json
import urllib.request
import urllib.error

from . import _base
from ._base import _encode_path, _get_ssl_context


def _download_file(path: str, save_path: str):
    url = f"{_base.SERVER_URL}{_encode_path(path)}"
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


def _download_file_post(path: str, payload: dict, save_path: str):
    """POST JSON 下载文件，用于一次提交多户 id 的批量导出。"""
    url = f"{_base.SERVER_URL}{_encode_path(path)}"
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Content-Type', 'application/json; charset=utf-8')
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
