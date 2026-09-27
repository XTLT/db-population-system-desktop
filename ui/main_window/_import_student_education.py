import os
from PyQt6.QtWidgets import QMessageBox, QFileDialog


def _import_student_education(self):
    path, _ = QFileDialog.getOpenFileName(
        self, "选择Excel文件", "",
        "Excel文件 (*.xlsx *.xls *.et)"
    )
    if not path:
        return
    if self.is_network_mode:
        import mimetypes
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        with open(path, 'rb') as f:
            file_data = f.read()
        content_type = mimetypes.guess_type(path)[0] or 'application/octet-stream'
        body = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(path)}"\r\n'
            f'Content-Type: {content_type}\r\n\r\n'
        ).encode('utf-8') + file_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')
        try:
            from network.client import _request_raw
            result = _request_raw('POST', '/api/students/import', body,
                                  f'multipart/form-data; boundary={boundary}')
            if result.get('imported') is not None:
                msg = f"导入完成！\n成功：{result.get('imported', 0)}条\n更新：{result.get('updated', 0)}条\n跳过：{result.get('skipped', 0)}条"
                if result.get("errors"):
                    msg += f"\n错误：{len(result['errors'])}条\n" + "\n".join(result["errors"][:5])
                QMessageBox.information(self, "导入结果", msg)
            else:
                QMessageBox.critical(self, "导入失败", result.get('error', '未知错误'))
        except Exception as e:
            QMessageBox.critical(self, "导入失败", str(e))
    else:
        from data.student_importer import import_student_education
        result = import_student_education(path)
        msg = f"导入完成！\n成功：{result['imported']}条\n更新：{result['updated']}条\n跳过：{result['skipped']}条"
        if result["errors"]:
            msg += f"\n错误：{len(result['errors'])}条\n" + "\n".join(result["errors"][:5])
        QMessageBox.information(self, "导入结果", msg)
