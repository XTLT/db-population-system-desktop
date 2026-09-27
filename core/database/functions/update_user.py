from .._base import get_session
from ..models.user import User


def update_user(user_id: str, **kwargs):
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
