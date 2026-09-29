from core.database import get_session, DisabilityCarePayment


def get_all_disability_care_payments(period: str = None, id_card: str = None) -> list:

    session = get_session()
    try:
        query = session.query(DisabilityCarePayment)
        if period:
            query = query.filter(DisabilityCarePayment.period == period)
        if id_card:
            query = query.filter(DisabilityCarePayment.id_card.like(f'%{id_card}%'))
        return query.order_by(DisabilityCarePayment.period.desc(), DisabilityCarePayment.name).all()
    finally:
        session.close()
