from ._request import _request


def api_add_household(data: dict) -> dict:
    return _request('POST', '/api/household/add', data)
