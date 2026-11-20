from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogDeletePhotoMixin:
    def _delete_photo(self):
        reply = QMessageBox.question(
            self, "确认删除", "确定要删除当前照片吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_photo(
                self.cbo_photo_type.currentText(),
                self.txt_id_card.text(),
                self.txt_social1.text(),
                self.txt_social2.text(),
                self.txt_social3.text()
            )
            if get_server_url():
                try:
                    from network.client import api_delete_photo_on_server
                    api_delete_photo_on_server(self.person.id, self.cbo_photo_type.currentText())
                except Exception as e:
                    QMessageBox.warning(self, "同步警告", f"照片已从本地删除，但同步删除服务器照片失败：\n{str(e)}")
            self._load_current_photo()
