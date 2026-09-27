from ._request import _request


def api_new_hu_hao() -> dict:
    return _request('GET', '/api/household/new_number')
