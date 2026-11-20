from .._imports import *
from .._consts import *
from ..funcs import *

from .m_init_mixin import ChangeProfileDialogMInitMixin
from .setup_ui_mixin import ChangeProfileDialogSetupUiMixin
from .toggle_mixin import ChangeProfileDialogToggleMixin
from .save_mixin import ChangeProfileDialogSaveMixin

class ChangeProfileDialog(ChangeProfileDialogMInitMixin, ChangeProfileDialogSetupUiMixin, ChangeProfileDialogToggleMixin, ChangeProfileDialogSaveMixin, QDialog):
    pass
