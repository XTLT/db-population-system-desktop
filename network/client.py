import os
import json
import mimetypes
import urllib.request
import urllib.parse
import urllib.error
import ssl
import shutil

SERVER_URL = ""
TOKEN = ""


def set_server_url(url: str):
    global SERVER_URL
    SERVER_URL = url.rstrip('/')


def get_server_url() -> str:
    return SERVER_URL


def set_token(token: str):
    global TOKEN
    TOKEN = token


def get_token() -> str:
    return TOKEN


def _get_ssl_context():
    ctx = ssl.create_default_context()
    # 允许自签名证书（必须先禁用 check_hostname，再设置 verify_mode）
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _request(method: str, path: str, data: dict = None) -> dict:
    url = f"{SERVER_URL}{path}"
    if data:
        req_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=req_data, method=method)
        req.add_header('Content-Type', 'application/json')
    else:
        req = urllib.request.Request(url, method=method)
    
    if TOKEN:
        req.add_header('Authorization', f'Bearer {TOKEN}')
    
    try:
        ctx = _get_ssl_context() if SERVER_URL.startswith('https') else None
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        try:
            msg = json.loads(body).get('error', body)
        except Exception:
            msg = body
        raise ConnectionError(f"服务器错误({e.code}): {msg}")
    except urllib.error.URLError as e:
        raise ConnectionError(f"无法连接服务器: {url}\n{e}")


def api_login(username: str, password: str) -> dict:
    return _request('POST', '/api/login', {'username': username, 'password': password})


def api_search(name: str) -> list:
    result = _request('GET', f'/api/search?name={urllib.parse.quote(name)}')
    return result.get('results', []) if isinstance(result, dict) else result


def api_family(hu_hao: str) -> list:
    result = _request('GET', f'/api/family/{hu_hao}')
    return result.get('members', []) if isinstance(result, dict) else result


def api_person(person_id: str) -> dict:
    result = _request('GET', f'/api/person/{person_id}')
    return result.get('person', result) if isinstance(result, dict) else result


def api_add_person(data: dict) -> dict:
    return _request('POST', '/api/person', data)


def api_check_duplicate(hu_hao: str, id_card: str) -> bool:
    result = _request('GET', f'/api/check_duplicate?hu_hao={urllib.parse.quote(hu_hao)}&id_card={urllib.parse.quote(id_card)}')
    return result.get('duplicate', False)


def api_update_education(person_id: str, data: dict) -> dict:
    return _request('PUT', f'/api/person/{person_id}/education', data)


def api_deleted_persons() -> list:
    return _request('GET', '/api/deleted')


def api_recover_person(deleted_id: str) -> dict:
    return _request('POST', f'/api/recover/{deleted_id}')


def api_students_search(school=None, grade=None, class_name=None, is_left_behind=None) -> list:
    params = []
    if school:
        params.append(f'school={urllib.parse.quote(school)}')
    if grade:
        params.append(f'grade={urllib.parse.quote(grade)}')
    if class_name:
        params.append(f'class_name={urllib.parse.quote(class_name)}')
    if is_left_behind:
        params.append(f'is_left_behind={urllib.parse.quote(is_left_behind)}')
    query = '&'.join(params)
    result = _request('GET', f'/api/students/search{"?" + query if query else ""}')
    return result.get('results', []) if isinstance(result, dict) else result


def api_new_hu_hao() -> dict:
    return _request('GET', '/api/household/new_number')


def api_add_household(data: dict) -> dict:
    return _request('POST', '/api/household/add', data)


def api_update_person(person_id: str, data: dict) -> dict:
    return _request('PUT', f'/api/person/{person_id}', data)


def api_delete_person(person_id: str) -> dict:
    return _request('DELETE', f'/api/person/{person_id}')


def api_migrate_person(person_id: str, data: dict) -> dict:
    return _request('POST', f'/api/person/{person_id}/migrate', data)


def api_students(school=None, grade=None, class_name=None, is_left_behind=None) -> list:
    params = []
    if school:
        params.append(f'school={urllib.parse.quote(school)}')
    if grade:
        params.append(f'grade={urllib.parse.quote(grade)}')
    if class_name:
        params.append(f'class_name={urllib.parse.quote(class_name)}')
    if is_left_behind:
        params.append(f'is_left_behind={urllib.parse.quote(is_left_behind)}')
    query = '&'.join(params)
    result = _request('GET', f'/api/students{"?" + query if query else ""}')
    return result.get('students', []) if isinstance(result, dict) else result


def api_stats() -> dict:
    return _request('GET', '/api/stats')


def api_promote_grades() -> dict:
    return _request('POST', '/api/students/promote')


def api_upload_photo(person_id: str, file_path: str, photo_type: str = "身份证") -> dict:
    url = f"{SERVER_URL}/api/person/{person_id}/photo"
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
    if TOKEN:
        req.add_header('Authorization', f'Bearer {TOKEN}')

    try:
        ctx = _get_ssl_context() if SERVER_URL.startswith('https') else None
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.URLError as e:
        raise ConnectionError(f"上传照片失败: {url}\n{e}")


def api_download_photo(person_id: str, save_path: str) -> bool:
    url = f"{SERVER_URL}/api/person/{person_id}/photo"
    req = urllib.request.Request(url, method='GET')
    if TOKEN:
        req.add_header('Authorization', f'Bearer {TOKEN}')

    try:
        ctx = _get_ssl_context() if SERVER_URL.startswith('https') else None
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            with open(save_path, 'wb') as f:
                shutil.copyfileobj(resp, f)
            return True
    except urllib.error.URLError as e:
        raise ConnectionError(f"下载照片失败: {url}\n{e}")


def api_delete_photo_on_server(person_id: str, photo_type: str = "身份证") -> dict:
    url = f"{SERVER_URL}/api/person/{person_id}/photo?photo_type={urllib.parse.quote(photo_type)}"
    req = urllib.request.Request(url, method='DELETE')
    if TOKEN:
        req.add_header('Authorization', f'Bearer {TOKEN}')

    try:
        ctx = _get_ssl_context() if SERVER_URL.startswith('https') else None
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.URLError as e:
        raise ConnectionError(f"删除服务器照片失败: {url}\n{e}")


def api_export_filtered(save_path: str, filters: dict = None, password: str = ""):
    url = f"{SERVER_URL}/api/export/excel"
    data = {'password': password}
    if filters:
        data['filters'] = filters
    req_data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=req_data, method='POST')
    req.add_header('Content-Type', 'application/json')
    if TOKEN:
        req.add_header('Authorization', f'Bearer {TOKEN}')

    ctx = _get_ssl_context() if SERVER_URL.startswith('https') else None
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


def _request_raw(method: str, path: str, body: bytes, content_type: str) -> dict:
    url = f"{SERVER_URL}{path}"
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header('Content-Type', content_type)
    if TOKEN:
        req.add_header('Authorization', f'Bearer {TOKEN}')
    try:
        ctx = _get_ssl_context() if SERVER_URL.startswith('https') else None
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.URLError as e:
        raise ConnectionError(f"请求失败: {url}\n{e}")


def _download_file(path: str, save_path: str):
    url = f"{SERVER_URL}{path}"
    req = urllib.request.Request(url, method='GET')
    if TOKEN:
        req.add_header('Authorization', f'Bearer {TOKEN}')
    try:
        ctx = _get_ssl_context() if SERVER_URL.startswith('https') else None
        with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
            with open(save_path, 'wb') as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
    except urllib.error.URLError as e:
        raise ConnectionError(f"下载失败: {url}\n{e}")


def test_connection() -> bool:
    try:
        url = f"{SERVER_URL}/api/health"
        ctx = _get_ssl_context() if SERVER_URL.startswith('https') else None
        req = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data.get('healthy', False) or data.get('status') == 'ok'
    except Exception as e:
        print(f"连接测试失败: {e}")
        return False
