import hashlib
import secrets

from .._base import get_session
from ..models.user import User
from .validate_password import validate_password


def change_user_password(user_id: str, old_password: str, new_password: str) -> tuple[bool, str]:
    valid, msg = validate_password(new_password)
    if not valid:
        return False, msg
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "用户不存在"
        salt, stored_hash = user.password_hash.split(":")
        if hashlib.sha256((salt + old_password).encode()).hexdigest() != stored_hash:
            return False, "原密码错误"
        new_salt = secrets.token_hex(16)
        new_hash = hashlib.sha256((new_salt + new_password).encode()).hexdigest()
        user.password_hash = f"{new_salt}:{new_hash}"
        session.commit()
        return True, ""
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
