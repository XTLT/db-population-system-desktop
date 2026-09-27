from .._base import get_session
from ..models.person import Person


def add_person(person: Person):
    session = get_session()
    try:
        session.add(person)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
