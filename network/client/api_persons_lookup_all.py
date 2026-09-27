from ._request import _request


def api_persons_lookup_all() -> list:
    """一次性获取所有人员关键字段，用于批量匹配"""
    result = _request('GET', '/api/persons/lookup-all')
    return result.get('persons', []) if isinstance(result, dict) else result
