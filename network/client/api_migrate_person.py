from ._request import _request


def api_migrate_person(person_id: str, data: dict) -> dict:
    return _request('POST', f'/api/person/{person_id}/migrate', data)
