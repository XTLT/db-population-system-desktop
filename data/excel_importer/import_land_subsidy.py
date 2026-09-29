import os
import secrets
from datetime import datetime

from core.database import get_session, Person, LandSubsidy
from core.utils import safe_str
from ._read_excel_robust import _read_excel_robust
from ._backfill_social_card import _backfill_social_card


def import_land_subsidy(file_path: str, subsidy_year: str = "", progress_callback=None) -> dict:
    """导入地力补贴数据

    只导入身份证号在数据库中存在的人员
    """

    df = _read_excel_robust(file_path)
    df = df.fillna("")

    header_row = -1
    for idx, row in df.iterrows():
        values = [str(v).strip() for v in row.values]
        if "姓名" in values and "身份证号" in values:
            header_row = idx
            break

    if header_row == -1:
        return {"imported": 0, "skipped": 0, "errors": ["未找到表头（姓名、身份证号）"], "total": 0, "not_found": []}

    main_headers = [str(v).strip() for v in df.iloc[header_row].values]

    if header_row + 1 < len(df):
        sub_headers = [str(v).strip() for v in df.iloc[header_row + 1].values]
    else:
        sub_headers = [""] * len(main_headers)

    col_map = {}
    for i, (main, sub) in enumerate(zip(main_headers, sub_headers)):
        if main:
            if sub:
                col_map[i] = f"{main}_{sub}"
            else:
                col_map[i] = main
        elif sub:
            col_map[i] = sub
        else:
            col_map[i] = f"col_{i}"

    data_df = df.iloc[header_row + 2:].reset_index(drop=True)
    data_df.columns = [col_map.get(i, f"col_{i}") for i in range(len(col_map))]

    total = len(data_df)
    imported = 0
    skipped = 0
    errors = []
    not_found = []
    session = get_session()

    # 获取数据库中所有身份证号
    existing_id_cards = set()
    person_map = {}
    try:
        persons = session.query(Person).all()
        existing_id_cards = {p.id_card for p in persons if p.id_card}
        person_map = {p.id_card: p for p in persons if p.id_card}
    except Exception:
        pass

    try:
        for idx, row in data_df.iterrows():
            try:
                name = safe_str(row.get("姓名", ""))
                id_card = safe_str(row.get("身份证号", ""))

                if not name and not id_card:
                    skipped += 1
                    continue

                # 检查身份证号是否在数据库中存在
                if id_card and id_card not in existing_id_cards:
                    not_found.append(f"{name}({id_card})")
                    skipped += 1
                    continue

                certified_area = ""
                for key in row.index:
                    if "确权颁证面积" in key or "确权颁发面积" in key:
                        certified_area = safe_str(row.get(key, ""))
                        break

                subsidy_area = ""
                for key in row.index:
                    if "补贴面积" in key:
                        val = safe_str(row.get(key, ""))
                        subsidy_area = val.replace("（亩）", "").replace("(亩)", "").strip()
                        break

                base_standard = ""
                for key in row.index:
                    if "基础补贴标准" in key:
                        val = safe_str(row.get(key, ""))
                        base_standard = val.replace("（元/亩）", "").replace("(元/亩)", "").strip()
                        break

                rape_area = ""
                for key in row.index:
                    if "其中种植油菜" in key and "面积" in key:
                        rape_area = safe_str(row.get(key, "")).strip()
                        break

                rape_amount = ""
                for key in row.index:
                    if "其中种植油菜" in key and "金额" in key:
                        rape_amount = safe_str(row.get(key, "")).strip()
                        break

                total_amount = ""
                for key in row.index:
                    if "补贴总金额" in key:
                        val = safe_str(row.get(key, ""))
                        total_amount = val.replace("（元）", "").replace("(元)", "").strip()
                        break

                if id_card and subsidy_year:
                    card = ""
                    for key in row.index:
                        if "卡号" in key:
                            card = safe_str(row.get(key, "")).strip()
                            break
                    person = person_map.get(id_card)
                    if person and card:
                        _backfill_social_card(person, "地力补贴" + subsidy_year, card)

                subsidy = LandSubsidy(
                    id=f"ls_{secrets.token_hex(8)}",
                    id_card=id_card,
                    name=name,
                    subsidy_year=subsidy_year,
                    certified_area=certified_area,
                    subsidy_area=subsidy_area,
                    base_standard=base_standard,
                    rape_area=rape_area,
                    rape_amount=rape_amount,
                    total_amount=total_amount,
                    import_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
                session.add(subsidy)
                imported += 1

                if progress_callback:
                    progress_callback(int((idx + 1) / total * 100))
            except Exception as e:
                skipped += 1
                errors.append(f"行{idx + header_row + 3}: {str(e)}")

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    return {"imported": imported, "skipped": skipped, "errors": errors, "total": total, "not_found": not_found}
