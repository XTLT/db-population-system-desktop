from .._imports import *
from .._consts import *
from ..funcs import *



class GradePromotionWorkerRunMixin:
    def run(self):
        try:
            if self.is_network:
                from network.client import api_promote_grades
                result = api_promote_grades()
                if result.get('success'):
                    self.finished.emit(result.get('count', 0))
                else:
                    self.error.emit(result.get('error', '升级失败'))
            else:
                from core.database import promote_all_grades
                count = promote_all_grades()
                self.finished.emit(count)
        except Exception as e:
            self.error.emit(str(e))
