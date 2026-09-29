from core.database import get_session, DibaoPayment


def delete_dibao_payment(record_id: str):

    session = get_session()
    try:
        record = session.query(DibaoPayment).filter(DibaoPayment.id == record_id).first()
        if record:
            session.delete(record)
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
