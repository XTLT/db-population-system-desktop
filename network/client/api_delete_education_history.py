from ._request import _request


def api_delete_education_history(person_id: str, history_id: str) -> dict:
    """删除一条就读历史记录（服务器 DELETE 接口）。"""
    return _request('DELETE', f'/api/person/{person_id}/education/history/{history_id}')
