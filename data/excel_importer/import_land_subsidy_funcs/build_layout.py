"""根据地力补贴表格布局，解析主表头、子表头与数据起始行。

探测 header_row 的下一行是否真为子表头：
  - 完全空白行 → 视为两表式的空行占位子表头
  - 该行在“姓名”“身份证号”列下都为空 → 是单位/量词子表头
  - 否则（姓名/身份证号列下已出现人名或证件号）→ 单表头模板，下一行就是首行数据
"""


def build_layout(df, header_row: int) -> dict:
    main_headers = [str(v).strip() for v in df.iloc[header_row].values]

    # 定位“姓名”“身份证号”在表头中的列位置（用于判定下一行是否为真子表头）
    name_pos = id_pos = -1
    for i, h in enumerate(main_headers):
        if h == "姓名" or h == "户主姓名":
            name_pos = i
        elif h == "身份证号":
            id_pos = i

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

    return {
        "main_headers": main_headers,
        "sub_headers": sub_headers,
        "data_start": data_start,
        "name_pos": name_pos,
        "id_pos": id_pos,
    }
