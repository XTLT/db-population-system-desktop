from .._base import get_session
from ..models.person import Person


def search_by_name(name: str) -> list[Person]:
    session = get_session()
    try:
        return session.query(Person).filter(Person.name.like(f"%{name}%")).all()
    finally:
        session.close()
