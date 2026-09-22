from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QProgressBar, QFileDialog, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QFont

from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR


class TreatmentPaymentImportWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, file_path: str, is_network_mode: bool):
        super().__init__()
        self.file_path = file_path
        self.is_network_mode = is_network_mode

    def run(self):
        try:
            if self.is_network_mode:
                import os
                import mimetypes
                from network.client import _request_raw

                boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
                with open(self.file_path, 'rb') as f:
                    file_data = f.read()
                content_type = mimetypes.guess_type(self.file_path)[0] or 'application/octet-stream'
                body = (
                    f'--{boundary}\r\n'
                    f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(self.file_path)}"\r\n'
                    f'Content-Type: {content_type}\r\n\r\n'
                ).encode('utf-8') + file_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')
                result = _request_raw('POST', '/api/treatment_payment/import', body,
                                      f'multipart/form-data; boundary={boundary}')
                self.finished.emit(result)
            else:
                from data.excel_importer import import_treatment_payment
                result = import_treatment_payment(self.file_path, self.progress.emit)
                self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class TreatmentPaymentImportDialog(QDialog):
    def __init__(self, is_network_mode: bool = False, parent=None):
        super().__init__(parent)
        self.is_network_mode = is_network_mode
        self.setWindowTitle("导入待遇发放数据")
        self.setFixedSize(450, 250)
        self.worker = None
        self._file_path = ""
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        font = QFont(FONT_NAME, FONT_SIZE)

        file_layout = QHBoxLayout()
        self.lbl_file = QLabel("未选择文件")
        self.lbl_file.setFont(font)
        btn_browse = QPushButton("选择文件")
        btn_browse.clicked.connect(self._browse)
        file_layout.addWidget(self.lbl_file)
        file_layout.addWidget(btn_browse)
        layout.addLayout(file_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.lbl_status = QLabel("")
        self.lbl_status.setFont(font)
        layout.addWidget(self.lbl_status)

        btn_layout = QHBoxLayout()
        btn_import = QPushButton("开始导入")
        btn_import.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 10px;")
        btn_import.clicked.connect(self._start_import)
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 10px;")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_import)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "",
            "Excel文件 (*.xlsx *.xls)"
        )
        if path:
            self._file_path = path
            self.lbl_file.setText(path)

    def _start_import(self):
        if not self._file_path:
            QMessageBox.warning(self, "提示", "请先选择Excel文件！")
            return

        self.lbl_status.setText("正在导入...")
        self.progress_bar.setValue(0)
        self.worker = TreatmentPaymentImportWorker(self._file_path, self.is_network_mode)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_progress(self, value):
        self.progress_bar.setValue(value)

    def _on_finished(self, result):
        msg = f"导入完成！\n成功：{result.get('imported', 0)}条\n跳过：{result.get('skipped', 0)}条"
        if result.get("errors"):
            msg += f"\n错误：{len(result['errors'])}条\n" + "\n".join(result["errors"][:5])
        not_found = result.get("not_found", [])
        if not_found:
            unique_not_found = list(set(not_found))
            msg += f"\n\n数据库中未找到的人员（{len(unique_not_found)}人）：\n"
            msg += "\n".join(unique_not_found[:20])
            if len(unique_not_found) > 20:
                msg += f"\n...等{len(unique_not_found)}人"
        self.lbl_status.setText("导入完成")
        QMessageBox.information(self, "导入结果", msg)
        self.accept()

    def _on_error(self, error_msg):
        self.lbl_status.setText("导入失败")
        QMessageBox.critical(self, "错误", f"导入失败：{error_msg}")