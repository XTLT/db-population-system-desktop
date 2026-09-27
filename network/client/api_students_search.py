import urllib.parse

from ._request import _request


def api_students_search(school=None, grade=None, class_name=None, is_left_behind=None) -> list:
    params = []
    if school:
        params.append(f'school={urllib.parse.quote(school)}')
    if grade:
        params.append(f'grade={urllib.parse.quote(grade)}')
    if class_name:
        params.append(f'class_name={urllib.parse.quote(class_name)}')
    if is_left_behind:
        params.append(f'is_left_behind={urllib.parse.quote(is_left_behind)}')
    query = '&'.join(params)
    result = _request('GET', f'/api/students/search{"?" + query if query else ""}')
    return result.get('results', []) if isinstance(result, dict) else result
