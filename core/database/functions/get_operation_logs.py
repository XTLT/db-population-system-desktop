from .._base import get_session
from ..models.operation_log import OperationLog


def get_operation_logs(limit: int = 100) -> list:
    session = get_session()
    try:
        return session.query(OperationLog).order_by(OperationLog.created_at.desc()).limit(limit).all()
    finally:
        session.close()
