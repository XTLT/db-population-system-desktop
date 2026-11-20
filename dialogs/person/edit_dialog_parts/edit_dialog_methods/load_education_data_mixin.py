from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogLoadEducationDataMixin:
    def _load_education_data(self):
        if get_server_url():
            try:
                from network.client import api_person
                data = api_person(self.person.id)
                edu_data = data.get('education')
                if edu_data:
                    self.txt_school.setText(edu_data.get('school_name', ''))
                    grade = edu_data.get('grade', '')
                    grade_set = False
                    for i in range(self.cbo_grade.count()):
                        if self.cbo_grade.itemData(i) == grade:
                            self.cbo_grade.setCurrentIndex(i)
                            grade_set = True
                            break
                    if not grade_set and grade:
                        for i in range(self.cbo_grade.count()):
                            if self.cbo_grade.itemText(i) == grade:
                                self.cbo_grade.setCurrentIndex(i)
                                grade_set = True
                                break
                    if not grade_set and grade:
                        self.cbo_grade.setEditText(grade)
                    self.txt_class.setText(edu_data.get('class_name', ''))
                    self.cbo_guardian.setCurrentText(edu_data.get('guardian', ''))
                    self.txt_guardian_phone.setText(edu_data.get('guardian_phone', ''))
                    self.cbo_is_left_behind.setCurrentText(edu_data.get('is_left_behind', '否'))
                    self.cbo_student_status.setCurrentText(edu_data.get('student_status', ''))
                    enrollment_date = edu_data.get('enrollment_date', '')
                    if enrollment_date:
                        try:
                            self.date_enrollment.setDate(QDate.fromString(enrollment_date, "yyyy-MM-dd"))
                        except Exception:
                            pass
                    self.txt_graduation_date.setText(edu_data.get('graduation_date', ''))
            except Exception:
                pass
            # 联网模式：从服务器读取就读历史记录并显示
            self.history_table.setColumnCount(0)
            self.history_table.setRowCount(0)
            try:
                from network.client import api_get_education_history
                history = api_get_education_history(self.person.id)
                headers = ["日期", "学校", "年级", "班级", "状态", "原因"]
                self.history_table.setColumnCount(len(headers))
                self.history_table.setHorizontalHeaderLabels(headers)
                self.history_table.setRowCount(len(history))
                for row_idx, h in enumerate(history):
                    values = [
                        h.get('change_date', ''),
                        h.get('school_name', ''),
                        h.get('grade', ''),
                        h.get('class_name', ''),
                        h.get('student_status', ''),
                        h.get('change_reason', ''),
                    ]
                    for col_idx, val in enumerate(values):
                        item = QTableWidgetItem(str(val) if val else "")
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        if col_idx == 0:
                            item.setData(Qt.ItemDataRole.UserRole, h.get('id', ''))
                        self.history_table.setItem(row_idx, col_idx, item)
                self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            except Exception:
                pass
        else:
            edu = get_student_education(self.person.id)
            if edu:
                self.txt_school.setText(edu.school_name)
                for i in range(self.cbo_grade.count()):
                    if self.cbo_grade.itemData(i) == edu.grade:
                        self.cbo_grade.setCurrentIndex(i)
                        break
                self.txt_class.setText(edu.class_name)
                self.cbo_guardian.setCurrentText(edu.guardian)
                self.txt_guardian_phone.setText(edu.guardian_phone)
                self.cbo_is_left_behind.setCurrentText(edu.is_left_behind)
                self.cbo_student_status.setCurrentText(edu.student_status)
                if edu.enrollment_date:
                    try:
                        self.date_enrollment.setDate(QDate.fromString(edu.enrollment_date, "yyyy-MM-dd"))
                    except Exception:
                        pass
                self.txt_graduation_date.setText(getattr(edu, 'graduation_date', '') or '')

            history = get_education_history(self.person.id)
            headers = ["日期", "学校", "年级", "班级", "状态", "原因"]
            self.history_table.setColumnCount(len(headers))
            self.history_table.setHorizontalHeaderLabels(headers)
            self.history_table.setRowCount(len(history))
            for row_idx, h in enumerate(history):
                values = [h.change_date, h.school_name, h.grade, h.class_name, h.student_status, h.change_reason]
                for col_idx, val in enumerate(values):
                    item = QTableWidgetItem(str(val) if val else "")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if col_idx == 0:
                        item.setData(Qt.ItemDataRole.UserRole, h.id)
                    self.history_table.setItem(row_idx, col_idx, item)
            self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
