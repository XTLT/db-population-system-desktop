from .._base import get_session
from ..models.student_education import StudentEducation


def delete_student_education(person_id: str):
    session = get_session()
    try:
        edu = session.query(StudentEducation).filter(StudentEducation.person_id == person_id).first()
        if edu:
            session.delete(edu)
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
