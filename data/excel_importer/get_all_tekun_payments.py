from core.database import get_session, TekunPayment


def get_all_tekun_payments(period: str = None, id_card: str = None) -> list:

    session = get_session()
    try:
        query = session.query(TekunPayment)
        if period:
            query = query.filter(TekunPayment.period == period)
        if id_card:
            query = query.filter(TekunPayment.id_card.like(f'%{id_card}%'))
        return query.order_by(TekunPayment.period.desc(), TekunPayment.name).all()
    finally:
        session.close()
