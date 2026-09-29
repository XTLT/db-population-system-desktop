from core.database import get_session, ElderlyAllowance


def get_all_elderly_allowances(period: str = None, id_card: str = None) -> list:

    session = get_session()
    try:
        query = session.query(ElderlyAllowance)
        if period:
            query = query.filter(ElderlyAllowance.period == period)
        if id_card:
            query = query.filter(ElderlyAllowance.id_card.like(f'%{id_card}%'))
        return query.order_by(ElderlyAllowance.period.desc(), ElderlyAllowance.name).all()
    finally:
        session.close()
