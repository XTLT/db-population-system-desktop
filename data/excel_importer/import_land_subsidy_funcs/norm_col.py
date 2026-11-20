"""去掉列名里的单位括号，便于别名匹配。"""

from .unit_regex import UNIT_RE


def norm_col(name: str) -> str:
    """去掉列名里的单位括号（如 （亩）/(元/亩)/(元)）。"""
    return UNIT_RE.sub("", str(name)).strip()
