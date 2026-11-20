"""edit_dialog（已按一方法一文件拆分，本文件只做总装与兼容导出）。"""

from .edit_dialog_parts._imports import *
from .edit_dialog_parts._consts import *
from .edit_dialog_parts.funcs import *
from .edit_dialog_parts.edit_dialog_methods import EditDialog

__all__ = ['EditDialog']
