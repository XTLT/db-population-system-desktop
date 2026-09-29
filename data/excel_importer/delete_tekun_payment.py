from core.database import get_session, TekunPayment


def delete_tekun_payment(record_id: str):

    session = get_session()
    try:
        record = session.query(TekunPayment).filter(TekunPayment.id == record_id).first()
        if record:
            session.delete(record)
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
