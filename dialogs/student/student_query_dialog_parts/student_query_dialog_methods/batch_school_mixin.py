from .._imports import *
from .._consts import *
from ..funcs import *



class StudentQueryDialogBatchSchoolMixin:
    def _batch_school(self):
        person_ids = self._get_selected_person_ids()
        if not person_ids:
            QMessageBox.warning(self, "提示", "请先选择学生！")
            return
        school = self.txt_batch_school.text().strip()
        if not school:
            QMessageBox.warning(self, "提示", "请输入学校名称！")
            return
        if get_server_url():
            try:
                from network.client import api_update_education
                for pid in person_ids:
                    api_update_education(pid, {'school_name': school})
                QMessageBox.information(self, "成功", f"已更新 {len(person_ids)} 名学生的学校！")
                self._search()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"批量更新失败：{str(e)}")
        else:
            batch_update_school(person_ids, school)
            QMessageBox.information(self, "成功", f"已更新 {len(person_ids)} 名学生的学校！")
            self._search()
