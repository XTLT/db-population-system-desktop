from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogSavePhotoToMixin:
    def _save_photo_to(self):
        from PyQt6.QtWidgets import QFileDialog
        path = get_photo_path(
            self.cbo_photo_type.currentText(),
            self.txt_id_card.text(),
            self.txt_social1.text(),
            self.txt_social2.text(),
            self.txt_social3.text()
        )
        if not path:
            QMessageBox.information(self, "提示", "没有可保存的照片！")
            return
        dest, _ = QFileDialog.getSaveFileName(
            self, "保存照片", "", "图片文件 (*.jpg *.jpeg *.png *.bmp)"
        )
        if dest:
            from data.photo_manager import export_photo
            if export_photo(path, dest):
                QMessageBox.information(self, "成功", f"照片已保存到：{dest}")
