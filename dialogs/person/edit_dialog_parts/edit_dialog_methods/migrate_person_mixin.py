from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogMigratePersonMixin:
    def _migrate_person(self):
        from dialogs.person.migration_dialog import MigrationDialog
        dialog = MigrationDialog(self.person.name, self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                if get_server_url():
                    from network.client import api_migrate_person
                    api_migrate_person(self.person.id, data)
                else:
                    migrate_person(
                        self.person.id,
                        data["date"],
                        data["place"],
                        data["reason"]
                    )
                QMessageBox.information(self, "成功", f"已将 {self.person.name} 标记为户籍迁出！")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"操作失败：{str(e)}")
