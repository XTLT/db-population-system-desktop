import urllib.parse

from ._request import _request


def api_search(name: str) -> list:
    result = _request('GET', f'/api/search?name={urllib.parse.quote(name)}')
    return result.get('results', []) if isinstance(result, dict) else result
