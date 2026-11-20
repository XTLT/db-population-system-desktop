"""地力补贴数据导入（只导入身份证号在数据库中存在的人员）。"""

from core.database import get_session

from .._read_excel_robust import _read_excel_robust
from .._backfill_social_card import _backfill_social_card
from .find_header_row import find_header_row
from .build_layout import build_layout
from .build_col_map import build_col_map
from .build_field_col import build_field_col
from .load_existing import load_existing
from .process_land_row import process_land_row


def import_land_subsidy(file_path: str, subsidy_year: str = "", progress_callback=None, dry_run: bool = False) -> dict:
    """导入地力补贴数据

    只导入身份证号在数据库中存在的人员
    """
    df = _read_excel_robust(file_path)
    df = df.fillna("")

    header_row = find_header_row(df)
    if header_row == -1:
        return {"imported": 0, "skipped": 0, "errors": ["未找到表头（姓名/户主姓名、身份证号）"], "total": 0, "not_found": []}

    layout = build_layout(df, header_row)
    main_headers = layout["main_headers"]
    sub_headers = layout["sub_headers"]
    data_start = layout["data_start"]
    name_pos = layout["name_pos"]
    id_pos = layout["id_pos"]

    col_map = build_col_map(main_headers, sub_headers)

    data_df = df.iloc[data_start:].reset_index(drop=True)
    data_df.columns = [col_map.get(i, f"col_{i}") for i in range(len(col_map))]

    field_col = build_field_col(data_df, name_pos, id_pos)

    total = len(data_df)
    imported = 0
    updated = 0
    skipped = 0
    errors = []
    not_found = []
    session = get_session()

    existing_id_cards, person_map, existing_by_key = load_existing(session, subsidy_year)

    try:
        for idx, row in data_df.iterrows():
            counts, not_found_entry, error = process_land_row(
                session, row, idx, total, field_col, subsidy_year,
                existing_id_cards, person_map, existing_by_key, data_start,
                progress_callback, _backfill_social_card,
            )
            imported += counts["imported"]
            updated += counts["updated"]
            skipped += counts["skipped"]
            if not_found_entry:
                not_found.append(not_found_entry)
            if error:
                errors.append(error)

        if dry_run:
            session.rollback()
        else:
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    return {"imported": imported, "updated": updated, "skipped": skipped, "errors": errors, "total": total, "not_found": not_found, "dry_run": dry_run}
