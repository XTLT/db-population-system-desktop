from .._base import get_session
from ..models.user import User


def get_all_users() -> list:
    session = get_session()
    try:
        return session.query(User).all()
    finally:
        session.close()
