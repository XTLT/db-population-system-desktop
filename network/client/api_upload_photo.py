import os
import json
import mimetypes
import urllib.request
import urllib.error

from . import _base
from ._base import _get_ssl_context


def api_upload_photo(person_id: str, file_path: str, photo_type: str = "身份证") -> dict:
    url = f"{_base.SERVER_URL}/api/person/{person_id}/photo"
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    content_type = mimetypes.guess_type(file_path)[0] or 'image/jpeg'

    with open(file_path, 'rb') as f:
        file_data = f.read()

    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="photo_type"\r\n\r\n'
        f'{photo_type}\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(file_path)}"\r\n'
        f'Content-Type: {content_type}\r\n\r\n'
    ).encode('utf-8') + file_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')

    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    if _base.TOKEN:
        req.add_header('Authorization', f'Bearer {_base.TOKEN}')

    try:
        ctx = _get_ssl_context() if _base.SERVER_URL.startswith('https') else None
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.URLError as e:
        raise ConnectionError(f"上传照片失败: {url}\n{e}")
