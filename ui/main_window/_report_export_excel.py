from PyQt6.QtWidgets import QHBoxLayout, QDialog, QMessageBox, QTableWidget, QFileDialog, QVBoxLayout, QTableWidgetItem, QAbstractItemView, QHeaderView, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.config import FONT_NAME, BTN_SAVE_COLOR, FONT_SIZE, BTN_CANCEL_COLOR


def _report_export_excel(self):

    try:
        from network.client import _request
        reports = _request('GET', '/api/reports')
    except Exception as e:
        QMessageBox.critical(self, "错误", f"获取报表列表失败：{e}")
        return

    if not reports:
        QMessageBox.warning(self, "提示", "没有已上传的报表")
        return

    dialog = QDialog(self)
    dialog.setWindowTitle("选择要导出的报表")
    dialog.setFixedSize(750, 450)
    layout = QVBoxLayout(dialog)

    table = QTableWidget()
    table.setFont(QFont(FONT_NAME, FONT_SIZE))
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    headers = ["报表名称", "上传者", "上传时间", "大小"]
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setRowCount(len(reports))
    for row_idx, r in enumerate(reports):
        name_item = QTableWidgetItem(r['original_name'])
        name_item.setData(Qt.ItemDataRole.UserRole, r['report_id'])
        name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(row_idx, 0, name_item)
        table.setItem(row_idx, 1, QTableWidgetItem(r['username']))
        table.setItem(row_idx, 2, QTableWidgetItem(r['upload_time']))
        size = r.get('file_size', 0)
        if size > 1024 * 1024:
            size_text = f"{size / 1024 / 1024:.1f} MB"
        elif size > 1024:
            size_text = f"{size / 1024:.1f} KB"
        else:
            size_text = f"{size} B"
        table.setItem(row_idx, 3, QTableWidgetItem(size_text))
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    layout.addWidget(table)

    btn_layout = QHBoxLayout()
    btn_download = QPushButton("下载")
    btn_download.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 8px 20px;")
    btn_logs = QPushButton("查看日志")
    btn_logs.setStyleSheet("background-color: #FF6600; color: white; padding: 8px 20px;")
    btn_close = QPushButton("关闭")
    btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px 20px;")
    btn_layout.addStretch()
    btn_layout.addWidget(btn_download)
    btn_layout.addWidget(btn_logs)
    btn_layout.addWidget(btn_close)
    layout.addLayout(btn_layout)

    def do_download():
        row = table.currentRow()
        if row < 0:
            QMessageBox.warning(dialog, "提示", "请选择一个报表")
            return
        report_id = table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        report_name = table.item(row, 0).text()
        save_path, _ = QFileDialog.getSaveFileName(
            dialog, "保存报表", report_name,
            "Excel文件 (*.xlsx *.xls *.et)"
        )
        if not save_path:
            return
        try:
            from network.client import _download_file
            _download_file(f'/api/reports/{report_id}/download', save_path)
            QMessageBox.information(dialog, "成功", f"已保存到：\n{save_path}")
        except Exception as e:
            QMessageBox.critical(dialog, "下载失败", str(e))

    def do_logs():
        row = table.currentRow()
        if row < 0:
            QMessageBox.warning(dialog, "提示", "请选择一个报表")
            return
        report_id = table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        self._show_report_logs(report_id, dialog)

    btn_download.clicked.connect(do_download)
    btn_logs.clicked.connect(do_logs)
    btn_close.clicked.connect(dialog.close)
    dialog.exec()
