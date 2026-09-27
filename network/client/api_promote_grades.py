from ._request import _request


def api_promote_grades() -> dict:
    return _request('POST', '/api/students/promote')
