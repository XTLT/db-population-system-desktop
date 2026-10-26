from ._request import _request


def api_get_education_history(person_id: str) -> list:
    """获取某人的就读历史记录（服务器 /education/history 接口）。"""
    result = _request('GET', f'/api/person/{person_id}/education/history')
    if isinstance(result, dict):
        return result.get('history', []) or []
    return []
