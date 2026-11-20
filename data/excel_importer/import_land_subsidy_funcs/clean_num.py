"""去掉数值里可能残留的单位括号。"""

from .unit_regex import UNIT_RE


def clean_num(val: str) -> str:
    """去掉数值里可能残留的单位括号。"""
    return UNIT_RE.sub("", str(val)).strip()
