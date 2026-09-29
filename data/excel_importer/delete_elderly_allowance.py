from core.database import get_session, ElderlyAllowance


def delete_elderly_allowance(record_id: str):

    session = get_session()
    try:
        record = session.query(ElderlyAllowance).filter(ElderlyAllowance.id == record_id).first()
        if record:
            session.delete(record)
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
