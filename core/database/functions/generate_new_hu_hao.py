from .._base import get_session
from ..models.person import Person


def generate_new_hu_hao() -> str:
    session = get_session()
    try:
        persons = session.query(Person).all()
        max_num = 0
        for p in persons:
            try:
                num = int(p.hu_hao)
                if num > max_num:
                    max_num = num
            except (ValueError, TypeError):
                pass
        return str(max_num + 1)
    finally:
        session.close()
