"""处理地力补贴表格中的单行数据。

返回 (counts, not_found_entry, error)：
  counts          —— {"imported": n, "updated": n, "skipped": n}
  not_found_entry —— 库外人员的 "姓名(身份证号)" 文本，或 None
  error           —— 该行异常文本，或 None
"""

import secrets
from datetime import datetime

from core.database import LandSubsidy
from core.utils import safe_str

from .clean_num import clean_num


def process_land_row(session, row, idx, total, field_col, subsidy_year, existing_id_cards,
                     person_map, existing_by_key, data_start, progress_callback,
                     backfill_social_card=None):
    def _cell(key):
        pos = field_col.get(key)
        if pos is None or pos >= len(row):
            return ""
        return safe_str(row.iloc[pos])

    counts = {"imported": 0, "updated": 0, "skipped": 0}

    try:
        name = _cell("name")
        id_card = _cell("id_card")

        if not name and not id_card:
            counts["skipped"] += 1
            return counts, None, None

        # 检查身份证号是否在数据库中存在
        if id_card and id_card not in existing_id_cards:
            counts["skipped"] += 1
            return counts, f"{name}({id_card})", None

        certified_area = clean_num(_cell("certified_area"))
        subsidy_area   = clean_num(_cell("subsidy_area"))
        base_standard  = clean_num(_cell("base_standard"))
        rape_area      = _cell("rape_area").strip()
        rape_amount    = _cell("rape_amount").strip()
        total_amount   = clean_num(_cell("total_amount"))
        phone          = _cell("phone").strip()
        bank_account   = _cell("bank_account").strip()
        bank_name      = _cell("bank_name").strip()
        land_time      = _cell("land_time").strip()
        rape_standard  = _cell("rape_standard").strip()

        if id_card and subsidy_year:
            card = _cell("card").strip()
            person = person_map.get(id_card)
            if person and card and backfill_social_card is not None:
                backfill_social_card(person, "地力补贴" + subsidy_year, card)

        existing = existing_by_key.get((id_card, subsidy_year))
        if existing is not None:
            # 同年同人已存在：覆盖更新，避免重复记录
            existing.id_card = id_card
            existing.name = name
            existing.subsidy_year = subsidy_year
            existing.certified_area = certified_area
            existing.subsidy_area = subsidy_area
            existing.base_standard = base_standard
            existing.rape_area = rape_area
            existing.rape_amount = rape_amount
            existing.total_amount = total_amount
            existing.phone = phone
            existing.bank_account = bank_account
            existing.bank_name = bank_name
            existing.land_time = land_time
            existing.rape_standard = rape_standard
            counts["updated"] += 1
        else:
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
                phone=phone,
                bank_account=bank_account,
                bank_name=bank_name,
                land_time=land_time,
                rape_standard=rape_standard,
                import_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
            session.add(subsidy)
        counts["imported"] += 1

        if progress_callback:
            progress_callback(int((idx + 1) / total * 100))
        return counts, None, None
    except Exception as e:
        counts["skipped"] += 1
        return counts, None, f"行{data_start + idx + 1}: {str(e)}"
