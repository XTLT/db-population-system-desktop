"""原模块的顶层函数 _col_letter。"""
from .._imports import *
from .._consts import *

def _col_letter(n):
    """1 → A, 2 → B, 27 → AA"""
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s
