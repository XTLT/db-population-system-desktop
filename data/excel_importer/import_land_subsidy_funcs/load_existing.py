"""读取库中已有人员与同年度地力补贴记录，供导入时判定与覆盖。"""

from core.database import Person, LandSubsidy


def load_existing(session, subsidy_year: str) -> tuple:
    """返回 (existing_id_cards, person_map, existing_by_key)。"""
    existing_id_cards = set()
    person_map = {}
    try:
        persons = session.query(Person).all()
        existing_id_cards = {p.id_card for p in persons if p.id_card}
        person_map = {p.id_card: p for p in persons if p.id_card}
    except Exception:
        pass

    # 同年同人去重：已存在该年度记录则覆盖更新（地力补贴一年一导入，不应重复）
    existing_by_key = {}
    try:
        if subsidy_year:
            for r in session.query(LandSubsidy).filter(LandSubsidy.subsidy_year == subsidy_year).all():
                if r.id_card:
                    existing_by_key[(r.id_card, r.subsidy_year)] = r
    except Exception:
        pass

    return existing_id_cards, person_map, existing_by_key
