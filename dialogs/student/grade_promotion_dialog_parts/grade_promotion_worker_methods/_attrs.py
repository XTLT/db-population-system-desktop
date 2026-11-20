from .._imports import *
from .._consts import *
from ..funcs import *



class GradePromotionWorkerAttrsMixin:
    finished = pyqtSignal(int)
    error = pyqtSignal(str)
