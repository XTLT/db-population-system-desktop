from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogDeletePersonMixin:
    def _delete_person(self):
        reply1 = QMessageBox.question(
            self, "确认删除",
            f"确定要删除人员 {self.person.name} 吗？\n删除后可在「找回」功能中恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply1 == QMessageBox.StandardButton.Yes:
            reply2 = QMessageBox.question(
                self, "再次确认",
                f"请再次确认：是否删除 {self.person.name}？\n此操作会将该人员移入回收站。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply2 == QMessageBox.StandardButton.Yes:
                try:
                    if get_server_url():
                        from network.client import api_delete_person
                        api_delete_person(self.person.id)
                    else:
                        from core.database import delete_person as do_delete
                        do_delete(self.person.id)
                    QMessageBox.information(self, "成功", f"已将 {self.person.name} 移入回收站！")
                    self.accept()
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"删除失败：{str(e)}")
