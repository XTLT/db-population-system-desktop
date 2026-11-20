from .._imports import *
from .._consts import *
from ..funcs import *



class GradePromotionWorkerMInitMixin:
    def __init__(self, is_network=False):
        super().__init__()
        self.is_network = is_network
