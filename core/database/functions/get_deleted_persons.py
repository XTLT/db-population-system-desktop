from .._base import get_session
from ..models.deleted_person import DeletedPerson


def get_deleted_persons() -> list:
    session = get_session()
    try:
        return session.query(DeletedPerson).all()
    finally:
        session.close()
