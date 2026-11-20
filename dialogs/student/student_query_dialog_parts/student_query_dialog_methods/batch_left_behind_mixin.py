from .._imports import *
from .._consts import *
from ..funcs import *



class StudentQueryDialogBatchLeftBehindMixin:
    def _batch_left_behind(self):
        person_ids = self._get_selected_person_ids()
        if not person_ids:
            QMessageBox.warning(self, "提示", "请先选择学生！")
            return
        value = self.cbo_batch_left.currentText()
        if get_server_url():
            try:
                from network.client import api_update_education
                for pid in person_ids:
                    api_update_education(pid, {'is_left_behind': value})
                QMessageBox.information(self, "成功", f"已设置 {len(person_ids)} 名学生的留守儿童状态！")
                self._search()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"批量设置失败：{str(e)}")
        else:
            batch_set_left_behind(person_ids, value)
            QMessageBox.information(self, "成功", f"已设置 {len(person_ids)} 名学生的留守儿童状态！")
            self._search()
