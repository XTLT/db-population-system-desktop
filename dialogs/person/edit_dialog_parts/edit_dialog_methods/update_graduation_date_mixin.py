from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogUpdateGraduationDateMixin:
    def _update_graduation_date(self, grade_code):
        grade_years = {
            'G1': 6, 'G2': 5, 'G3': 4, 'G4': 3, 'G5': 2, 'G6': 1,
            'G7': 3, 'G8': 2, 'G9': 1,
            'G10': 3, 'G11': 2, 'G12': 1,
        }
        total_years = grade_years.get(grade_code, 0)
        if total_years > 0:
            from core.utils import calculate_enrollment_date
            enrollment_date = calculate_enrollment_date(grade_code)
            if enrollment_date:
                try:
                    enroll_year = int(enrollment_date[:4])
                    grad_year = enroll_year + total_years
                    self.txt_graduation_date.setText(f"{grad_year}-06-30")
                except Exception:
                    pass
