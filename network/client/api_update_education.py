from ._request import _request


def api_update_education(person_id: str, data: dict) -> dict:
    return _request('PUT', f'/api/person/{person_id}/education', data)
