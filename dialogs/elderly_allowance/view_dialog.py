"""view_dialog（已按一方法一文件拆分，本文件只做总装与兼容导出）。"""

from .view_dialog_parts._imports import *
from .view_dialog_parts._consts import *
from .view_dialog_parts.funcs import *
from .view_dialog_parts.elderly_allowance_view_dialog_methods import ElderlyAllowanceViewDialog

__all__ = ['ElderlyAllowanceViewDialog']
