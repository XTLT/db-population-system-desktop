from .._imports import *
from .._consts import *
from ..funcs import *

from ._attrs import GradePromotionWorkerAttrsMixin
from .m_init_mixin import GradePromotionWorkerMInitMixin
from .run_mixin import GradePromotionWorkerRunMixin

class GradePromotionWorker(GradePromotionWorkerMInitMixin, GradePromotionWorkerAttrsMixin, GradePromotionWorkerRunMixin, QThread):
    pass
