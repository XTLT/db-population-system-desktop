from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogSaveEducationMixin:
    def _save_education(self):
        school = self.txt_school.text().strip()
        grade_code = self.cbo_grade.currentData()
        grade_display = self.cbo_grade.currentText().strip() if not grade_code else ''
        class_name = self.txt_class.text().strip()
        graduation_date = self.txt_graduation_date.text().strip()

        if get_server_url():
            from network.client import api_update_education
            edu_data = {
                'school_name': school,
                'grade': grade_code or grade_display or '',
                'class_name': class_name,
                'guardian': self.cbo_guardian.currentText().strip(),
                'guardian_phone': self.txt_guardian_phone.text().strip(),
                'is_left_behind': self.cbo_is_left_behind.currentText(),
                'student_status': self.cbo_student_status.currentText(),
                'enrollment_date': self.date_enrollment.date().toString("yyyy-MM-dd"),
                'graduation_date': graduation_date,
            }
            try:
                api_update_education(self.person.id, edu_data)
            except Exception as e:
                QMessageBox.warning(self, "同步警告", f"就读信息保存到服务器失败：\n{str(e)}")
        elif school or grade_code or class_name:
            edu = StudentEducation(
                id=f"edu_{self.person.id}",
                person_id=self.person.id,
                id_card=self.person.id_card,
                school_name=school,
                grade=grade_code or "",
                class_name=class_name,
                guardian=self.cbo_guardian.currentText().strip(),
                guardian_phone=self.txt_guardian_phone.text().strip(),
                is_left_behind=self.cbo_is_left_behind.currentText(),
                student_status=self.cbo_student_status.currentText(),
                enrollment_date=self.date_enrollment.date().toString("yyyy-MM-dd"),
                graduation_date=graduation_date,
            )
            save_student_education(edu)
        else:
            delete_student_education(self.person.id)
