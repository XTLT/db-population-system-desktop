from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QProgressBar, QComboBox, QMessageBox, QFileDialog, QRadioButton
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR
from data.excel_importer import import_excel_full, import_excel_incremental, generate_template
class ImportWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, file_path: str, mode: str):
        super().__init__()
        self.file_path = file_path
        self.mode = mode

    def run(self):
        try:
            if self.mode == "full":
                result = import_excel_full(self.file_path, self.progress.emit)
            else:
                result = import_excel_incremental(self.file_path, self.progress.emit)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
class ImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Excel导入")
        self.setFixedSize(450, 300)
        self.worker = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        from PyQt6.QtGui import QFont
        font = QFont(FONT_NAME, FONT_SIZE)

        mode_label = QLabel("导入模式：")
        mode_label.setFont(font)
        layout.addWidget(mode_label)

        self.radio_full = QRadioButton("全量导入（覆盖所有数据）")
        self.radio_full.setFont(font)
        self.radio_full.setChecked(True)
        self.radio_incremental = QRadioButton("增量导入（新增+更新）")
        self.radio_incremental.setFont(font)
        layout.addWidget(self.radio_full)
        layout.addWidget(self.radio_incremental)

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
        btn_template = QPushButton("生成模板")
        btn_template.clicked.connect(self._generate_template)
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 10px;")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_import)
        btn_layout.addWidget(btn_template)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        self._file_path = ""

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "",
            "Excel文件 (*.xlsx *.xls)"
        )
        if path:
            self._file_path = path
            self.lbl_file.setText(path)

    def _generate_template(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "保存模板", "人口信息导入模板.xlsx",
            "Excel文件 (*.xlsx)"
        )
        if path:
            generate_template(path)
            QMessageBox.information(self, "成功", f"模板已生成：{path}")

    def _start_import(self):
        if not self._file_path:
            QMessageBox.warning(self, "提示", "请先选择Excel文件！")
            return
        mode = "full" if self.radio_full.isChecked() else "incremental"
        self.lbl_status.setText("正在导入...")
        self.progress_bar.setValue(0)
        self.worker = ImportWorker(self._file_path, mode)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_progress(self, value):
        self.progress_bar.setValue(value)

    def _on_finished(self, result):
        msg = f"导入完成！\n成功：{result['imported']}条"
        if "updated" in result:
            msg += f"\n更新：{result['updated']}条"
        msg += f"\n跳过：{result['skipped']}条"
        if result["errors"]:
            msg += f"\n错误：{len(result['errors'])}条\n" + "\n".join(result["errors"][:5])
        self.lbl_status.setText("导入完成")
        QMessageBox.information(self, "导入结果", msg)
        self.accept()

    def _on_error(self, error_msg):
        self.lbl_status.setText("导入失败")
        QMessageBox.critical(self, "错误", f"导入失败：{error_msg}")
