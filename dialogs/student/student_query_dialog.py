"""student_query_dialog（已按一方法一文件拆分，本文件只做总装与兼容导出）。"""

from .student_query_dialog_parts._imports import *
from .student_query_dialog_parts._consts import *
from .student_query_dialog_parts.funcs import *
from .student_query_dialog_parts.student_query_dialog_methods import StudentQueryDialog

__all__ = ['StudentQueryDialog']
