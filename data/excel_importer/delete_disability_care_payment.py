from core.database import get_session, DisabilityCarePayment


def delete_disability_care_payment(record_id: str):

    session = get_session()
    try:
        record = session.query(DisabilityCarePayment).filter(DisabilityCarePayment.id == record_id).first()
        if record:
            session.delete(record)
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
