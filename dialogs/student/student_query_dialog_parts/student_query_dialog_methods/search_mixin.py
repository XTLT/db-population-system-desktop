from .._imports import *
from .._consts import *
from ..funcs import *



class StudentQueryDialogSearchMixin:
    def _search(self):
        school = self.txt_school.text().strip() or None
        grade = self.cbo_grade.currentData() or None
        class_name = self.txt_class.text().strip() or None
        left_behind = self.cbo_left_behind.currentText() or None

        if get_server_url():
            try:
                from network.client import api_students_search
                students = api_students_search(school, grade, class_name, left_behind)
            except Exception:
                students = []
        else:
            students = search_students(school, grade, class_name, left_behind)
        self._load_data(students)
