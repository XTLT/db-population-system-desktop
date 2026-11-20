"""原模块的顶层函数 _to_amount。"""
from .._imports import *
from .._consts import *

def _to_amount(value) -> float:
    try:
        return float(str(value or "").replace(",", "").strip())
    except (TypeError, ValueError):
        return 0.0
