from PyQt6.QtWidgets import QDialog, QMessageBox, QTableWidget, QVBoxLayout, QTableWidgetItem, QAbstractItemView, QHeaderView, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.config import FONT_NAME, FONT_SIZE, BTN_CANCEL_COLOR


def _show_report_logs_dialog(self, report_id, report_name, parent):

    try:
        from network.client import _request
        data = _request('GET', f'/api/reports/{report_id}/logs')
    except Exception as e:
        QMessageBox.critical(parent, "错误", f"获取日志失败：{e}")
        return

    dialog = QDialog(parent)
    dialog.setWindowTitle(f"操作日志 - {report_name}")
    dialog.setFixedSize(850, 500)
    layout = QVBoxLayout(dialog)

    table = QTableWidget()
    table.setFont(QFont(FONT_NAME, FONT_SIZE))
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    headers = ["时间", "用户", "操作", "详情", "IP"]
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)

    all_logs = data.get('db_logs', []) + data.get('file_logs', [])
    all_logs.sort(key=lambda x: x.get('time', ''), reverse=True)
    table.setRowCount(len(all_logs))
    for row_idx, l in enumerate(all_logs):
        for col_idx, key in enumerate(['time', 'user', 'action', 'detail', 'ip']):
            item = QTableWidgetItem(str(l.get(key, '')))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row_idx, col_idx, item)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    layout.addWidget(table)

    btn_close = QPushButton("关闭")
    btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px 20px;")
    layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)
    btn_close.clicked.connect(dialog.close)
    dialog.exec()
