"""在 DataFrame 中定位表头行（姓名/户主姓名 + 身份证号）。"""


def find_header_row(df) -> int:
    """返回表头所在行号，找不到返回 -1。"""
    for idx, row in df.iterrows():
        values = [str(v).strip() for v in row.values]
        if ("姓名" in values or "户主姓名" in values) and "身份证号" in values:
            return idx
    return -1
