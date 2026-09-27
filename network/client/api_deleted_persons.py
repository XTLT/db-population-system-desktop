from ._request import _request


def api_deleted_persons() -> list:
    return _request('GET', '/api/deleted')
