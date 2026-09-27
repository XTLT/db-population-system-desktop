import hashlib
import secrets

from .._base import get_session
from ..models.user import User
from .validate_password import validate_password


def create_user(username: str, password: str, real_name: str = "", role: str = "user") -> User:
    from datetime import datetime
    valid, msg = validate_password(password)
    if not valid:
        raise ValueError(msg)
    session = get_session()
    try:
        existing = session.query(User).filter(User.username == username).first()
        if existing:
            raise ValueError("用户名已存在")
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
        user = User(
            id=f"user_{secrets.token_hex(8)}",
            username=username,
            password_hash=f"{salt}:{password_hash}",
            real_name=real_name,
            role=role,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        session.add(user)
        session.commit()
        return user
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
