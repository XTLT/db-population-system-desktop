"""user_dialog（已按一方法一文件拆分，本文件只做总装与兼容导出）。"""

from .user_dialog_parts._imports import *
from .user_dialog_parts._consts import *
from .user_dialog_parts.funcs import *
from .user_dialog_parts.login_dialog_methods import LoginDialog
from .user_dialog_parts.change_profile_dialog_methods import ChangeProfileDialog

__all__ = ['LoginDialog', 'ChangeProfileDialog']
