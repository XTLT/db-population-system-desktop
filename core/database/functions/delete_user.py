from .._base import get_session
from ..models.user import User


def delete_user(user_id: str):
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            session.delete(user)
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
