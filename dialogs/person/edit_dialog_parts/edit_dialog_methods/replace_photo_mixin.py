from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogReplacePhotoMixin:
    def _replace_photo(self):
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "选择要上传的照片", "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp)"
        )
        if path:
            save_photo(
                path,
                self.cbo_photo_type.currentText(),
                self.txt_id_card.text(),
                self.txt_social1.text(),
                self.txt_social2.text(),
                self.txt_social3.text()
            )
            if get_server_url():
                try:
                    from network.client import api_upload_photo
                    api_upload_photo(self.person.id, path, self.cbo_photo_type.currentText())
                except Exception as e:
                    QMessageBox.warning(self, "同步警告", f"照片已保存到本地，但同步到服务器失败：\n{str(e)}")
            self._load_current_photo()
