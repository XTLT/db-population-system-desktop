from .._base import get_session
from ..models.person import Person


def get_family_members(hu_hao: str) -> list[Person]:
    session = get_session()
    try:
        return session.query(Person).filter(Person.hu_hao == hu_hao).all()
    finally:
        session.close()
