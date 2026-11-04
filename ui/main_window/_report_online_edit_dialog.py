"""本地在线编辑窗口：不依赖浏览器，用 desktop 内嵌 mTLS 客户端证书直连服务器。

替代原 webbrowser.open 方式（浏览器缺客户端证书会报 ERR_BAD_SSL_CLIENT_AUTH_CERT）。
数据流：
  GET  /api/reports/<id>/data   → {headers, rows}（Bearer token）
  POST /api/reports/<id>/save   → {success}（Bearer token）
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QHeaderView, QAbstractItemView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.config import FONT_NAME, BTN_ADD_COLOR, FONT_SIZE, BTN_CANCEL_COLOR


class ReportEditDialog(QDialog):
    """报表在线编辑对话框（本地表格，可编辑单元格后保存回服务器）"""

    def __init__(self, report_id: str, report_name: str, parent=None):
        super().__init__(parent)
        self.report_id = report_id
        self.report_name = report_name
        self.setWindowTitle(f"在线编辑 - {report_name}")
        self.resize(1000, 620)
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.lbl_status = QLabel("正在加载报表数据...")
        self.lbl_status.setStyleSheet("color: #666; font-size: 13px; padding: 4px 0;")
        layout.addWidget(self.lbl_status)

        self.table = QTableWidget()
        self.table.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
            | QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        layout.addWidget(self.table, 1)

        btn_row = QHBoxLayout()
        self.btn_save = QPushButton("保存")
        self.btn_save.setStyleSheet(
            f"background-color: {BTN_ADD_COLOR}; color: white; font-weight: bold; padding: 8px 20px;"
        )
        self.btn_save.clicked.connect(self._save)
        btn_close = QPushButton("关闭")
        btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px 20px;")
        btn_close.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _load_data(self):
        try:
            from network.client import _request
            data = _request('GET', f'/api/reports/{self.report_id}/data')
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取报表数据失败：{e}")
            self.reject()
            return
        headers = data.get('headers', [])
        rows = data.get('rows', [])
        self._fill_table(headers, rows)
        self.lbl_status.setText(f"已加载 {len(rows)} 行数据（双击单元格编辑，修改后点保存）")

    def _fill_table(self, headers, rows):
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                self.table.setItem(r, c, item)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setDefaultSectionSize(28)

    def _collect_data(self):
        """收集表头与全部单元格数据（与服务器保存接口约定一致）"""
        headers = []
        for c in range(self.table.columnCount()):
            header_item = self.table.horizontalHeaderItem(c)
            headers.append(header_item.text() if header_item else '')

        rows = []
        for r in range(self.table.rowCount()):
            row = []
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                row.append(item.text() if item else '')
            rows.append(row)
        return headers, rows

    def _save(self):
        headers, rows = self._collect_data()
        if not headers:
            QMessageBox.warning(self, "提示", "报表没有表头，无法保存")
            return
        self.btn_save.setEnabled(False)
        self.lbl_status.setText("正在保存...")
        try:
            from network.client import _request
            _request('POST', f'/api/reports/{self.report_id}/save',
                     data={'headers': headers, 'rows': rows})
        except Exception as e:
            self.btn_save.setEnabled(True)
            self.lbl_status.setText("保存失败")
            QMessageBox.critical(self, "错误", f"保存失败：{e}")
            return
        self.btn_save.setEnabled(True)
        self.lbl_status.setText(f"保存成功（{len(rows)} 行）")
        QMessageBox.information(self, "提示", f"保存成功（{len(rows)} 行）")
