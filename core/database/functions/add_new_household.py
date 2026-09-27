from .._base import get_session
from ..models.person import Person


def add_new_household(hu_hao: str, name: str, id_card: str, relation: str = "户主", **kwargs) -> Person:
    session = get_session()
    try:
        existing = session.query(Person).filter(Person.hu_hao == hu_hao).first()
        if existing:
            raise ValueError(f"户号 {hu_hao} 已存在")
        from core.utils import calculate_age
        person = Person(
            id=f"p_{hu_hao}_{id_card}",
            hu_hao=hu_hao,
            id_card=id_card,
            name=name,
            age=calculate_age(id_card),
            relation=relation,
            address=kwargs.get("address", ""),
            phone=kwargs.get("phone", ""),
            land_area=kwargs.get("land_area", ""),
            local_welfare_forest_area=kwargs.get("local_welfare_forest_area", ""),
            national_welfare_forest_area=kwargs.get("national_welfare_forest_area", ""),
            commercial_forest_area=kwargs.get("commercial_forest_area", ""),
        )
        session.add(person)
        session.commit()
        return person
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
