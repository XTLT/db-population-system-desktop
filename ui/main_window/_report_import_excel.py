import os
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QInputDialog


def _report_import_excel(self):
    path, _ = QFileDialog.getOpenFileName(
        self, "选择Excel文件", "",
        "Excel文件 (*.xlsx *.xls *.et)"
    )
    if not path:
        return

    report_name = os.path.basename(path)
    name, ok = QInputDialog.getText(self, "报表名称", "请输入报表名称：", text=report_name)
    if not ok or not name.strip():
        return

    with open(path, 'rb') as f:
        file_data = f.read()

    import mimetypes
    content_type = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="name"\r\n\r\n'
        f'{name.strip()}\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="{report_name}"\r\n'
        f'Content-Type: {content_type}\r\n\r\n'
    ).encode('utf-8') + file_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')

    try:
        from network.client import _request_raw
        result = _request_raw('POST', '/api/reports/upload', body,
                              f'multipart/form-data; boundary={boundary}')
        if result.get('success'):
            QMessageBox.information(self, "成功", f"报表已上传：\n{name.strip()}")
        else:
            QMessageBox.critical(self, "失败", result.get('error', '上传失败'))
    except Exception as e:
        QMessageBox.critical(self, "上传失败", str(e))
