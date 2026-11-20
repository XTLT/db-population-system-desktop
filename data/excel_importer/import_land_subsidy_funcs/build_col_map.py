"""把主表头/子表头合并成列索引 -> 列名映射。"""


def build_col_map(main_headers, sub_headers) -> dict:
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
    return col_map
