from core.database import get_session, PensionInsurance


def delete_pension_insurance(record_id: str):

    session = get_session()
    try:
        record = session.query(PensionInsurance).filter(PensionInsurance.id == record_id).first()
        if record:
            session.delete(record)
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
