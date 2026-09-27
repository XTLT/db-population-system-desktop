from ._request import _request


def api_person(person_id: str) -> dict:
    result = _request('GET', f'/api/person/{person_id}')
    return result.get('person', result) if isinstance(result, dict) else result
