from ._request import _request


def api_stats() -> dict:
    return _request('GET', '/api/stats')
