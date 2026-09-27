from .._base import get_session
from ..models.education_history import EducationHistory


def get_education_history(person_id: str) -> list:
    session = get_session()
    try:
        return session.query(EducationHistory).filter(
            EducationHistory.person_id == person_id
        ).order_by(EducationHistory.change_date.desc()).all()
    finally:
        session.close()
