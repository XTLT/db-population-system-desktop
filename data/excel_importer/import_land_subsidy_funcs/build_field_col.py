"""按列位置建立 字段 -> 列索引 映射（姓名/身份证号用位置，其余用别名表匹配）。"""

from .field_aliases import LAND_FIELD_ALIASES
from .norm_col import norm_col


def build_field_col(data_df, name_pos: int, id_pos: int) -> dict:
    field_col = {}
    if name_pos >= 0:
        field_col["name"] = name_pos
    if id_pos >= 0:
        field_col["id_card"] = id_pos
    norm_cols = [norm_col(c) for c in data_df.columns]
    used_positions = set(field_col.values())
    for field, aliases in LAND_FIELD_ALIASES.items():
        for i, cn in enumerate(norm_cols):
            if i in used_positions:
                continue
            if any(alias in cn for alias in aliases):
                field_col[field] = i
                used_positions.add(i)
                break
    return field_col
