from ._request import _request


def api_add_person(data: dict) -> dict:
    return _request('POST', '/api/person', data)
