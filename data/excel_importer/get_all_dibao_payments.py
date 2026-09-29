from core.database import get_session, DibaoPayment


def get_all_dibao_payments(period: str = None, id_card: str = None) -> list:

    session = get_session()
    try:
        query = session.query(DibaoPayment)
        if period:
            query = query.filter(DibaoPayment.period == period)
        if id_card:
            query = query.filter(DibaoPayment.id_card.like(f'%{id_card}%'))
        return query.order_by(DibaoPayment.period.desc(), DibaoPayment.name).all()
    finally:
        session.close()
