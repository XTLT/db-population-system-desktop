from PyQt6.QtWidgets import QHBoxLayout, QDialog, QLabel, QMessageBox, QTableWidget, QVBoxLayout, QTableWidgetItem, QAbstractItemView, QHeaderView, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.config import FONT_NAME, BTN_ADD_COLOR, FONT_SIZE, BTN_CANCEL_COLOR
from network.client import get_server_url


def _report_online_edit(self):

    if not get_server_url():
        QMessageBox.warning(self, "提示", "请先连接服务器后再使用在线编辑功能")
        return

    is_admin = (self.current_user or {}).get('role') == 'admin'

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
    dialog.setWindowTitle("选择报表进行在线编辑")
    dialog.setFixedSize(700, 400)
    dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
    layout = QVBoxLayout(dialog)

    def fill_table():
        """用当前 reports 列表重建表格"""
        table.setRowCount(len(reports))
        for row_idx, r in enumerate(reports):
            name_item = QTableWidgetItem(r['original_name'])
            name_item.setData(Qt.ItemDataRole.UserRole, r['report_id'])
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row_idx, 0, name_item)
            table.setItem(row_idx, 1, QTableWidgetItem(r['username']))
            table.setItem(row_idx, 2, QTableWidgetItem(r['upload_time']))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    if not reports:
        lbl = QLabel("没有已上传的报表，请先通过「导入Excel」上传报表")
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
    fill_table()
    layout.addWidget(table)

    btn_layout = QHBoxLayout()
    btn_open = QPushButton("打开编辑")
    btn_open.setStyleSheet(f"background-color: {BTN_ADD_COLOR}; color: white; font-weight: bold; padding: 8px 20px;")
    btn_close = QPushButton("关闭")
    btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px 20px;")
    btn_layout.addStretch()
    btn_layout.addWidget(btn_open)
    if is_admin:
        btn_delete = QPushButton("删除选中报表")
        btn_delete.setStyleSheet("background-color: #CC0000; color: white; padding: 8px 20px;")
        btn_delete.setToolTip("仅管理员可见：删除上传的报表文件（不可恢复）")
        btn_layout.addWidget(btn_delete)
    btn_layout.addWidget(btn_close)
    layout.addLayout(btn_layout)

    def do_open():
        row = table.currentRow()
        if row < 0:
            QMessageBox.warning(dialog, "提示", "请选择一个报表")
            return
        report_id = table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        report_name = table.item(row, 0).text()
        from ui.main_window._report_online_edit_dialog import ReportEditDialog
        dlg = ReportEditDialog(report_id, report_name, dialog)
        dlg.exec()

    def do_delete():
        row = table.currentRow()
        if row < 0:
            QMessageBox.warning(dialog, "提示", "请先选择一个报表")
            return
        report_id = table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        report_name = table.item(row, 0).text()
        if QMessageBox.question(
            dialog, "确认删除",
            f"确定删除报表「{report_name}」？\n删除后文件不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:
            return
        try:
            from network.client import _request
            _request('DELETE', f'/api/reports/{report_id}')
        except Exception as e:
            QMessageBox.critical(dialog, "错误", f"删除失败：{e}")
            return
        QMessageBox.information(dialog, "提示", f"已删除报表「{report_name}」")
        # 刷新列表
        try:
            reports.clear()
            reports.extend(_request('GET', '/api/reports'))
        except Exception:
            reports.clear()
        if reports:
            fill_table()
        else:
            QMessageBox.information(dialog, "提示", "报表已全部删除")
            dialog.reject()
            return

    btn_open.clicked.connect(do_open)
    if is_admin:
        btn_delete.clicked.connect(do_delete)
    btn_close.clicked.connect(dialog.reject)
    table.doubleClicked.connect(do_open)
    dialog.exec()
