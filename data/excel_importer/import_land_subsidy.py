import os
import re
import secrets
from datetime import datetime

from core.database import get_session, Person, LandSubsidy
from core.utils import safe_str
from ._read_excel_robust import _read_excel_robust
from ._backfill_social_card import _backfill_social_card


# 列名别名兼容表：同时识别“模板列名”与“导出/旧表短名”
# key=内部字段，value=可能出现的列名（去掉单位括号后做子串匹配）
_LAND_FIELD_ALIASES = {
    "certified_area": ["确权颁证面积", "确权颁发面积"],
    "subsidy_area":   ["补贴面积"],
    "base_standard":  ["基础补贴标准"],
    "rape_area":      ["其中种植油菜面积", "油菜面积"],
    "rape_amount":    ["其中种植油菜金额", "油菜金额"],
    "total_amount":   ["补贴总金额"],
    "card":           ["卡号"],
}

_UNIT_RE = re.compile(r"[（(][^）)]*[）)]")


def _norm_col(name: str) -> str:
    """去掉列名里的单位括号（如 （亩）/(元/亩)/(元)），便于别名匹配。"""
    return _UNIT_RE.sub("", str(name)).strip()


def _clean_num(val: str) -> str:
    """去掉数值里可能残留的单位括号。"""
    return _UNIT_RE.sub("", str(val)).strip()


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

    # 定位“姓名”“身份证号”在表头中的列位置（用于判定下一行是否为真子表头）
    name_pos = id_pos = -1
    for i, h in enumerate(main_headers):
        if h == "姓名":
            name_pos = i
        elif h == "身份证号":
            id_pos = i

    # 探测 header_row 的下一行是否真为子表头：
    #  - 完全空白行 → 视为两表式的空行占位子表头
    #  - 该行在“姓名”“身份证号”列下都为空 → 是单位/量词子表头
    #  - 否则（姓名/身份证号列下已出现人名或证件号）→ 单表头模板，下一行就是首行数据
    data_start = header_row + 1
    if header_row + 1 < len(df):
        nxt = [str(v).strip() for v in df.iloc[header_row + 1].values]
        name_val = nxt[name_pos] if 0 <= name_pos < len(nxt) else ""
        id_val = nxt[id_pos] if 0 <= id_pos < len(nxt) else ""
        all_blank = all(v == "" for v in nxt)
        row_looks_like_data = bool(name_val) or bool(id_val)
        if all_blank or not row_looks_like_data:
            sub_headers = nxt
            data_start = header_row + 2
        else:
            sub_headers = [""] * len(main_headers)
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

    data_df = df.iloc[data_start:].reset_index(drop=True)
    data_df.columns = [col_map.get(i, f"col_{i}") for i in range(len(col_map))]

    # 按列位置建立 字段->列索引 映射（姓名/身份证号用位置，其余用别名表匹配）
    field_col = {}
    if name_pos >= 0:
        field_col["name"] = name_pos
    if id_pos >= 0:
        field_col["id_card"] = id_pos
    norm_cols = [_norm_col(c) for c in data_df.columns]
    used_positions = set(field_col.values())
    for field, aliases in _LAND_FIELD_ALIASES.items():
        for i, cn in enumerate(norm_cols):
            if i in used_positions:
                continue
            if any(alias in cn for alias in aliases):
                field_col[field] = i
                used_positions.add(i)
                break

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
                def _cell(key):
                    pos = field_col.get(key)
                    if pos is None or pos >= len(row):
                        return ""
                    return safe_str(row.iloc[pos])

                name = _cell("name")
                id_card = _cell("id_card")

                if not name and not id_card:
                    skipped += 1
                    continue

                # 检查身份证号是否在数据库中存在
                if id_card and id_card not in existing_id_cards:
                    not_found.append(f"{name}({id_card})")
                    skipped += 1
                    continue

                certified_area = _clean_num(_cell("certified_area"))
                subsidy_area   = _clean_num(_cell("subsidy_area"))
                base_standard  = _clean_num(_cell("base_standard"))
                rape_area      = _cell("rape_area").strip()
                rape_amount    = _cell("rape_amount").strip()
                total_amount   = _clean_num(_cell("total_amount"))

                if id_card and subsidy_year:
                    card = _cell("card").strip()
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
                errors.append(f"行{data_start + idx + 1}: {str(e)}")

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    return {"imported": imported, "skipped": skipped, "errors": errors, "total": total, "not_found": not_found}
