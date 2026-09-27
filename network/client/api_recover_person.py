from ._request import _request


def api_recover_person(deleted_id: str) -> dict:
    return _request('POST', f'/api/recover/{deleted_id}')
