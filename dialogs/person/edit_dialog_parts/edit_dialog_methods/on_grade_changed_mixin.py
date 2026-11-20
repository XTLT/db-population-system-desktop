from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogOnGradeChangedMixin:
    def _on_grade_changed(self, index):
        grade_code = self.cbo_grade.currentData()
        if grade_code:
            from core.utils import calculate_enrollment_date
            enrollment_date = calculate_enrollment_date(grade_code)
            if enrollment_date:
                try:
                    self.date_enrollment.setDate(QDate.fromString(enrollment_date, "yyyy-MM-dd"))
                except Exception:
                    pass
            self._update_graduation_date(grade_code)
