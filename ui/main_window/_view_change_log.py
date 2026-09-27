from PyQt6.QtWidgets import QHBoxLayout, QDialog, QLabel, QMessageBox, QTableWidget, QVBoxLayout, QTableWidgetItem, QAbstractItemView, QHeaderView, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.config import FONT_NAME, BTN_SAVE_COLOR, FONT_SIZE, BTN_CANCEL_COLOR
from network.client import get_server_url


def _view_change_log(self):

    if not get_server_url():
        QMessageBox.warning(self, "提示", "请先连接服务器后查看日志")
        return

    self.setCursor(Qt.CursorShape.WaitCursor)
    try:
        from network.client import _request
        reports = _request('GET', '/api/reports')
    except Exception as e:
        self.setCursor(Qt.CursorShape.ArrowCursor)
        QMessageBox.critical(self, "错误", f"获取报表列表失败：{e}")
        return
    finally:
        self.setCursor(Qt.CursorShape.ArrowCursor)

    dialog = QDialog(self)
    dialog.setWindowTitle("选择报表查看操作日志")
    dialog.setFixedSize(750, 450)
    layout = QVBoxLayout(dialog)

    if not reports:
        lbl = QLabel("没有已上传的报表")
        lbl.setStyleSheet("color: #999; font-size: 14px; padding: 20px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        btn_close = QPushButton("关闭")
        btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px 20px;")
        btn_close.clicked.connect(dialog.reject)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)
        dialog.exec()
        return

    table = QTableWidget()
    table.setFont(QFont(FONT_NAME, FONT_SIZE))
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    headers = ["报表名称", "上传者", "上传时间"]
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
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    layout.addWidget(table)

    btn_layout = QHBoxLayout()
    btn_view = QPushButton("查看日志")
    btn_view.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 8px 20px;")
    btn_close = QPushButton("关闭")
    btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px 20px;")
    btn_layout.addStretch()
    btn_layout.addWidget(btn_view)
    btn_layout.addWidget(btn_close)
    layout.addLayout(btn_layout)

    def do_view():
        row = table.currentRow()
        if row < 0:
            QMessageBox.warning(dialog, "提示", "请选择一个报表")
            return
        report_id = table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        report_name = table.item(row, 0).text()
        self._show_report_logs_dialog(report_id, report_name, dialog)

    btn_view.clicked.connect(do_view)
    table.doubleClicked.connect(do_view)
    btn_close.clicked.connect(dialog.reject)
    dialog.exec()
