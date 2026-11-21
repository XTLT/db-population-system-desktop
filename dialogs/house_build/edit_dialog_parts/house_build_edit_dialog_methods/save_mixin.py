from .._imports import *
from .._consts import *
from ..funcs import *


class HouseBuildEditDialogSaveMixin:
    def _save(self):
        payload = self._collect_data()
        if payload is None:
            return
        try:
            if self.app_id:
                result = api_house_build_update(self.app_id, payload)
            else:
                result = api_house_build_create(payload)
        except Exception as e:
            QMessageBox.warning(self, "提示", f"保存失败：{e}")
            return

        saved = (result or {}).get('data') or result or {}
        new_id = saved.get('id') or self.app_id
        if new_id:
            self.app_id = new_id
        self.txt_app_no.setText(saved.get('app_no', self.txt_app_no.text()))
        QMessageBox.information(
            self, "完成",
            '已保存。申请编号：%s' % (saved.get('app_no') or self.txt_app_no.text() or ''),
        )
        self.accept()
