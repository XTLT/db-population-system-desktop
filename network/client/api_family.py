from ._request import _request


def api_family(hu_hao: str) -> list:
    result = _request('GET', f'/api/family/{hu_hao}')
    return result.get('members', []) if isinstance(result, dict) else result
