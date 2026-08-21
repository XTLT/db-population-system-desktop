from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QLineEdit, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime

from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR


class TreatmentPaymentViewDialog(QDialog):
    def __init__(self, is_network_mode: bool = False, is_admin: bool = False, parent=None):
        super().__init__(parent)
        self.is_network_mode = is_network_mode
        self.is_admin = is_admin
        self.setWindowTitle("待遇发放数据")
        self.setFixedSize(800, 600)
        self._setup_ui()
        try:
            self._load_data()
        except Exception as e:
            QMessageBox.warning(self, "提示", f"加载数据时出错：{e}")

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()
        lbl_search = QLabel("搜索姓名：")
        lbl_search.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_search = QLineEdit()
        self.txt_search.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_search.setPlaceholderText("输入姓名搜索...")
        filter_layout.addWidget(lbl_search)
        filter_layout.addWidget(self.txt_search)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        headers = ["姓名", "银行账号", "金额", "导入时间"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_delete = QPushButton("删除选中")
        btn_delete.setStyleSheet(f"background-color: #CC0000; color: white; padding: 8px;")
        btn_delete.setEnabled(self.is_admin)
        btn_export = QPushButton("导出Excel")
        btn_export.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; padding: 8px;")
        btn_close = QPushButton("关闭")
        btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px;")
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_export)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        self.txt_search.textChanged.connect(lambda: self._load_data())
        btn_delete.clicked.connect(self._do_delete)
        btn_export.clicked.connect(self._do_export)
        btn_close.clicked.connect(self.reject)

    def _load_data(self):
        try:
            search = self.txt_search.text().strip()

            if self.is_network_mode:
                try:
                    from network.client import _request
                    params = {}
                    if search:
                        params['search'] = search
                    data = _request('GET', '/api/treatment_payment', params)
                    payments = data.get('payments', [])
                except Exception as e:
                    print(f"网络获取数据失败: {e}")
                    payments = []
            else:
                from data.excel_importer import get_all_treatment_payments
                payments = get_all_treatment_payments()
                if search:
                    payments = [p for p in payments if search in p.name]

            self.table.setRowCount(len(payments))
            for row_idx, p in enumerate(payments):
                item_name = QTableWidgetItem(p.name)
                item_name.setData(Qt.ItemDataRole.UserRole, p.id)
                self.table.setItem(row_idx, 0, item_name)
                self.table.setItem(row_idx, 1, QTableWidgetItem(p.bank_account))
                self.table.setItem(row_idx, 2, QTableWidgetItem(p.amount))
                self.table.setItem(row_idx, 3, QTableWidgetItem(p.import_time))

            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        except Exception as e:
            print(f"加载数据失败: {e}")

    def _do_delete(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "提示", "请先选择要删除的记录")
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除选中的 {len(selected) // self.table.columnCount()} 条记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            rows = set()
            for item in selected:
                rows.add(item.row())

            row_ids = []
            for row in rows:
                id_item = self.table.item(row, 0)
                if id_item:
                    row_ids.append(id_item.data(Qt.ItemDataRole.UserRole))

            if self.is_network_mode:
                from network.client import _request
                for rid in row_ids:
                    if rid:
                        _request('DELETE', f'/api/treatment_payment/{rid}')
            else:
                from data.excel_importer import delete_treatment_payment
                for rid in row_ids:
                    if rid:
                        delete_treatment_payment(rid)

            self._load_data()
            QMessageBox.information(self, "提示", "删除成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除失败：{e}")

    def _do_export(self):
        try:
            search = self.txt_search.text().strip()

            if self.is_network_mode:
                from network.client import _request
                params = {}
                if search:
                    params['search'] = search
                data = _request('GET', '/api/treatment_payment', params)
                payments = data.get('payments', [])
            else:
                from data.excel_importer import get_all_treatment_payments
                payments = get_all_treatment_payments()
                if search:
                    payments = [p for p in payments if search in p.name]

            if not payments:
                QMessageBox.warning(self, "提示", "没有数据可导出")
                return

            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出Excel", f"待遇发放_{datetime.now().strftime('%Y%m%d')}.xlsx",
                "Excel文件 (*.xlsx)"
            )
            if not file_path:
                return

            import pandas as pd
            data = []
            for p in payments:
                data.append({
                    "姓名": p.name,
                    "银行账号": p.bank_account,
                    "金额": p.amount,
                    "导入时间": p.import_time,
                })

            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            QMessageBox.information(self, "提示", f"导出成功！\n共 {len(payments)} 条记录")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败：{e}")