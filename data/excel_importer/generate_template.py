import pandas as pd

from core.config import EXCEL_TEMPLATE_COLUMNS
from ._auto_fit_columns import _auto_fit_columns


def generate_template(file_path: str):
    df = pd.DataFrame(columns=EXCEL_TEMPLATE_COLUMNS)
    df.to_excel(file_path, index=False, engine="openpyxl")
    # 模板按表头长度预设列宽，便于直接填写
    _auto_fit_columns(file_path, min_width=12, max_width=30)
