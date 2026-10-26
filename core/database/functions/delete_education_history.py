from .._base import get_session
from ..models.education_history import EducationHistory


def delete_education_history(history_id: str) -> bool:
    """删除一条就读历史记录（本地模式）。"""
    session = get_session()
    try:
        h = session.query(EducationHistory).filter(
            EducationHistory.id == history_id
        ).first()
        if not h:
            return False
        session.delete(h)
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()
