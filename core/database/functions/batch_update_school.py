from .._base import get_session
from ..models.student_education import StudentEducation


def batch_update_school(person_ids: list, school_name: str):
    session = get_session()
    try:
        for pid in person_ids:
            edu = session.query(StudentEducation).filter(StudentEducation.person_id == pid).first()
            if edu:
                edu.school_name = school_name
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
