from ._request import _request


def api_delete_person(person_id: str) -> dict:
    return _request('DELETE', f'/api/person/{person_id}')
