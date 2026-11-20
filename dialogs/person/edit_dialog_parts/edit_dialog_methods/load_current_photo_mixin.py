from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogLoadCurrentPhotoMixin:
    def _load_current_photo(self):
        path = get_photo_path(
            self.cbo_photo_type.currentText(),
            self.txt_id_card.text(),
            self.txt_social1.text(),
            self.txt_social2.text(),
            self.txt_social3.text()
        )
        if not path and get_server_url():
            try:
                from network.client import api_download_photo
                import tempfile
                tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                tmp.close()
                if api_download_photo(self.person.id, tmp.name):
                    save_photo(
                        tmp.name,
                        self.cbo_photo_type.currentText(),
                        self.txt_id_card.text(),
                        self.txt_social1.text(),
                        self.txt_social2.text(),
                        self.txt_social3.text()
                    )
                    path = get_photo_path(
                        self.cbo_photo_type.currentText(),
                        self.txt_id_card.text(),
                        self.txt_social1.text(),
                        self.txt_social2.text(),
                        self.txt_social3.text()
                    )
                os.unlink(tmp.name)
            except Exception:
                pass
        self.lbl_photo.clear()
        if path:
            pixmap = QPixmap(path)
            self.lbl_photo.setPixmap(pixmap.scaled(200, 150, Qt.AspectRatioMode.KeepAspectRatio))
            status = get_photo_status(
                self.txt_id_card.text(),
                self.txt_social1.text(),
                self.txt_social2.text(),
                self.txt_social3.text()
            )
            self.lbl_photo_status.setText(status)
        else:
            self.lbl_photo_status.setText("暂无照片")
