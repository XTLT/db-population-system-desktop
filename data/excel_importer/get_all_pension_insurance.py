from core.database import get_session, PensionInsurance


def get_all_pension_insurance(period: str = None, id_card: str = None) -> list:

    session = get_session()
    try:
        query = session.query(PensionInsurance)
        if period:
            query = query.filter(PensionInsurance.period == period)
        if id_card:
            query = query.filter(PensionInsurance.id_card.like(f'%{id_card}%'))
        return query.order_by(PensionInsurance.period.desc(), PensionInsurance.name).all()
    finally:
        session.close()
