"""add_dialog（已按一方法一文件拆分，本文件只做总装与兼容导出）。"""

from .add_dialog_parts._imports import *
from .add_dialog_parts._consts import *
from .add_dialog_parts.funcs import *
from .add_dialog_parts.add_dialog_methods import AddDialog

__all__ = ['AddDialog']
