from ._request import _request


def api_login(username: str, password: str) -> dict:
    return _request('POST', '/api/login', {'username': username, 'password': password})
