from .._imports import *
from .._consts import *
from ..funcs import *



class StudentQueryDialogLoadDataMixin:
    def _load_data(self, students=None):
        if students is None:
            if get_server_url():
                try:
                    from network.client import api_students
                    students = api_students()
                except Exception:
                    students = []
            else:
                students = get_all_students()

        headers = ["选择", "姓名", "身份证号", "学校", "年级", "班级", "监护人", "留守儿童", "状态"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(students))

        for row_idx, s in enumerate(students):
            if isinstance(s, dict):
                person_id = s.get('person_id', '')
                name = s.get('name', '')
                id_card = s.get('id_card', '')
                school_name = s.get('school_name', '')
                grade = s.get('grade', '')
                class_name = s.get('class_name', '')
                guardian = s.get('guardian', '')
                is_left_behind = s.get('is_left_behind', '')
                student_status = s.get('student_status', '')
                grade_display = GRADE_DISPLAY.get(grade, grade)
            else:
                person_id = s.person_id
                person = self._get_person(s.person_id)
                name = person.name if person else ""
                id_card = s.id_card
                school_name = s.school_name
                grade = s.grade
                class_name = s.class_name
                guardian = s.guardian
                is_left_behind = s.is_left_behind
                student_status = s.student_status
                grade_display = GRADE_DISPLAY.get(s.grade, s.grade)
            values = [name, id_card, school_name, grade_display, class_name, guardian, is_left_behind, student_status]
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            check_item.setCheckState(Qt.CheckState.Unchecked)
            check_item.setData(Qt.ItemDataRole.UserRole, person_id)
            check_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, check_item)
            for col_idx, val in enumerate(values):
                item = QTableWidgetItem(str(val) if val else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, col_idx + 1, item)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
