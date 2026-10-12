import os

import pandas as pd


def _read_excel_robust(file_path: str, header=None):
    """读取 Excel 文件，自动检测格式和引擎"""
    ext = os.path.splitext(file_path)[1].lower()
    engines = (['openpyxl', 'xlrd'] if ext == '.xlsx'
               else ['xlrd', 'openpyxl'] if ext == '.xls'
               else ['openpyxl', 'xlrd'])
    for engine in engines:
        try:
            return pd.read_excel(file_path, dtype=str, header=header, engine=engine)
        except Exception:
            continue
    try:
        return pd.read_csv(file_path, dtype=str, header=header, encoding='utf-8')
    except Exception:
        return pd.read_csv(file_path, dtype=str, header=header, encoding='gbk')


def _read_excel_with_header(file_path: str, known_columns, max_scan: int = 12):
    """自动定位表头行并读取。

    known_columns: 该模板已知列名列表（新列定义）。
    1) 先探测读前 max_scan 行（header=None, dtype=str）；
    2) 逐行统计该行非空单元格值与 known_columns 的精确匹配数（strip 后过滤 "" 与 "nan"）；
    3) 取匹配数最大的行作为表头行；最大匹配数 < 2 则回退 header=0；
    4) 用该行号调 _read_excel_robust 返回完整 df。
    """
    known = [str(c).strip() for c in known_columns]
    known_set = set(known)

    raw = _read_excel_robust(file_path, header=None)
    if raw is None:
        return _read_excel_robust(file_path, header=0)

    best_row = 0
    best_score = 0
    scan = raw.head(max_scan)
    for i in range(len(scan)):
        row_vals = scan.iloc[i].tolist()
        matched = set()
        for v in row_vals:
            s = "" if v is None else str(v).strip()
            if s == "" or s.lower() == "nan":
                continue
            if s in known_set:
                matched.add(s)
        if len(matched) > best_score:
            best_score = len(matched)
            best_row = i

    header_row = best_row if best_score >= 2 else 0
    return _read_excel_robust(file_path, header=header_row)
