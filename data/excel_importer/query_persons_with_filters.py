from core.database import get_session, Person
from core.utils import calculate_age
from data.excel_area_fields import (
    apply_land_area_filter,
    apply_local_welfare_forest_filter,
    apply_national_welfare_forest_filter,
    apply_commercial_forest_filter,
)


def query_persons_with_filters(filters: dict) -> list:
    session = get_session()
    try:
        query = session.query(Person)

        if filters.get("name"):
            query = query.filter(Person.name.contains(filters["name"]))
        if filters.get("address"):
            query = query.filter(Person.address.contains(filters["address"]))
        if filters.get("is_dead") and filters["is_dead"] != "全部":
            query = query.filter(Person.is_dead == filters["is_dead"])
        relation = filters.get("relation", [])
        if relation:
            query = query.filter(Person.relation.in_(relation))
        disability = filters.get("disability", [])
        if disability:
            query = query.filter(Person.disability.in_(disability))
        if filters.get("dis_level"):
            dis_level = filters["dis_level"]
            if isinstance(dis_level, list) and dis_level:
                query = query.filter(Person.dis_level.in_(dis_level))
            elif isinstance(dis_level, str) and dis_level != "全部":
                query = query.filter(Person.dis_level == dis_level)
        poor_type = filters.get("poor_type", [])
        if poor_type:
            query = query.filter(Person.poor_type.in_(poor_type))
        if filters.get("dibao") and filters["dibao"] != "全部":
            query = query.filter(Person.dibao == filters["dibao"])
        if filters.get("jisheng") and filters["jisheng"] != "全部":
            query = query.filter(Person.jisheng == filters["jisheng"])
        if filters.get("tekun") and filters["tekun"] != "全部":
            query = query.filter(Person.tekun == filters["tekun"])
        if filters.get("tekun_type"):
            tekun_type = filters["tekun_type"]
            if isinstance(tekun_type, list) and tekun_type:
                query = query.filter(Person.tekun_type.in_(tekun_type))
            elif isinstance(tekun_type, str) and tekun_type != "全部":
                query = query.filter(Person.tekun_type == tekun_type)
        land = filters.get("land_area", "全部")
        query = apply_land_area_filter(query, land, Person)
        local_welfare = filters.get("local_welfare_forest_area", "全部")
        query = apply_local_welfare_forest_filter(query, local_welfare, Person)
        national_welfare = filters.get("national_welfare_forest_area", "全部")
        query = apply_national_welfare_forest_filter(query, national_welfare, Person)
        commercial = filters.get("commercial_forest_area", "全部")
        query = apply_commercial_forest_filter(query, commercial, Person)

        persons = query.all()

        if filters.get("age_min") or filters.get("age_max"):
            age_min = int(filters["age_min"]) if filters.get("age_min") else 0
            age_max = int(filters["age_max"]) if filters.get("age_max") else 999
            filtered = []
            for p in persons:
                age = -1
                if p.age:
                    try:
                        age = int(p.age)
                    except (ValueError, TypeError):
                        pass
                if age < 0 and p.id_card:
                    age_str = calculate_age(p.id_card)
                    if age_str:
                        try:
                            age = int(age_str)
                        except (ValueError, TypeError):
                            pass
                if age >= 0 and age_min <= age <= age_max:
                    filtered.append(p)
            persons = filtered

        return persons
    finally:
        session.close()
