from .._base import get_session
from ..models.person import Person


def get_person_count() -> int:
    session = get_session()
    try:
        return session.query(Person).count()
    finally:
        session.close()
