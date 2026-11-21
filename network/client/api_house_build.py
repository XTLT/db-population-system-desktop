"""宅基地建房申请接口（列表/详情/增改删/身份证预填/导出下载）。"""

from urllib.parse import urlencode

from ._request import _request
from ._download_file import _download_file


def api_house_build_list(keyword: str = '', status: str = '', year: str = '',
                         group_name: str = '', page: int = 1, page_size: int = 20) -> dict:
    params = {
        'keyword': keyword, 'status': status, 'year': year,
        'group_name': group_name, 'page': page, 'page_size': page_size,
    }
    params = {k: v for k, v in params.items() if v not in ('', None)}
    return _request('GET', '/api/persons/house-build/list?' + urlencode(params))


def api_house_build_get(app_id: str) -> dict:
    return _request('GET', f'/api/persons/house-build/{app_id}')


def api_house_build_create(data: dict) -> dict:
    return _request('POST', '/api/persons/house-build', data)


def api_house_build_update(app_id: str, data: dict) -> dict:
    return _request('PUT', f'/api/persons/house-build/{app_id}', data)


def api_house_build_delete(app_id: str) -> dict:
    return _request('DELETE', f'/api/persons/house-build/{app_id}')


def api_house_build_prefill(id_card: str) -> dict:
    return _request('GET', '/api/persons/house-build/prefill?' + urlencode({'id_card': id_card}))


def api_house_build_download(app_id: str, fmt: str, save_path: str):
    _download_file(f'/api/persons/house-build/{app_id}/export?fmt={fmt}', save_path)
