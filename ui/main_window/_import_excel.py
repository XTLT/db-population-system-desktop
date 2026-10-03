import os
from PyQt6.QtWidgets import QMessageBox, QFileDialog
from dialogs.import_export.import_dialog import ImportDialog


def _import_excel(self):
    if self.is_network_mode:
        path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "",
            "Excel文件 (*.xlsx *.xls)"
        )
        if not path:
            return
        import mimetypes
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        with open(path, 'rb') as f:
            file_data = f.read()
        content_type = mimetypes.guess_type(path)[0] or 'application/octet-stream'
        body = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="mode"\r\n\r\n'
            f'incremental\r\n'
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(path)}"\r\n'
            f'Content-Type: {content_type}\r\n\r\n'
        ).encode('utf-8') + file_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')
        try:
            from network.client import _request_raw
            result = _request_raw('POST', '/api/import/excel', body,
                                  f'multipart/form-data; boundary={boundary}')
            if result.get('imported') is not None:
                msg = f"导入完成！\n成功：{result.get('imported', 0)}条\n更新：{result.get('updated', 0)}条\n跳过：{result.get('skipped', 0)}条"
                errors = result.get('errors') or []
                if errors:
                    msg += f"\n\n跳过明细（共{len(errors)}条）：\n" + "\n".join(errors[:50])
                    if len(errors) > 50:
                        msg += f"\n…共{len(errors)}条，其余见日志"
                QMessageBox.information(self, "导入结果", msg)
            else:
                QMessageBox.critical(self, "导入失败", result.get('error', '未知错误'))
        except Exception as e:
            QMessageBox.critical(self, "导入失败", str(e))
    else:
        dialog = ImportDialog(self)
        if dialog.exec():
            self._refresh_status()
