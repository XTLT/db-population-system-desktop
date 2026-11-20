from .._imports import *
from .._consts import *
from ..funcs import *

from .m_init_mixin import GradePromotionDialogMInitMixin
from .setup_ui_mixin import GradePromotionDialogSetupUiMixin
from .promote_mixin import GradePromotionDialogPromoteMixin
from .on_finished_mixin import GradePromotionDialogOnFinishedMixin
from .on_error_mixin import GradePromotionDialogOnErrorMixin

class GradePromotionDialog(GradePromotionDialogMInitMixin, GradePromotionDialogSetupUiMixin, GradePromotionDialogPromoteMixin, GradePromotionDialogOnFinishedMixin, GradePromotionDialogOnErrorMixin, QDialog):
    pass
