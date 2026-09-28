from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QLineEdit, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime

from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR


class TekunViewDialog(QDialog):
    def __init__(self, is_network_mode: bool = False, is_admin: bool = False, parent=None):
        super().__init__(parent)
        self.is_network_mode = is_network_mode
        self.is_admin = is_admin
        self.setWindowTitle("特困数据")
        self.setFixedSize(1100, 600)
        self._setup_ui()
        try:
            self._load_data()
        except Exception as e:
            QMessageBox.warning(self, "提示", f"加载数据时出错：{e}")

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()
        lbl_period = QLabel("费款所属期：")
        lbl_period.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_period = QLineEdit()
        self.txt_period.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_period.setPlaceholderText("如：202606")
        self.txt_period.setMaximumWidth(120)

        lbl_id_card = QLabel("身份证号：")
        lbl_id_card.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_id_card = QLineEdit()
        self.txt_id_card.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_id_card.setPlaceholderText("身份证号搜索")
        self.txt_id_card.setMaximumWidth(180)

        btn_search = QPushButton("查询")
        btn_search.setFont(QFont(FONT_NAME, FONT_SIZE))
        btn_search.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; padding: 6px 16px;")
        btn_search.clicked.connect(self._load_data)

        filter_layout.addWidget(lbl_period)
        filter_layout.addWidget(self.txt_period)
        filter_layout.addWidget(lbl_id_card)
        filter_layout.addWidget(self.txt_id_card)
        filter_layout.addWidget(btn_search)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        headers = ["费款所属期", "姓名", "身份证号", "所属村", "银行账号", "金额", "支付标志", "导入来源"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_delete = QPushButton("删除选中")
        btn_delete.setStyleSheet("background-color: #CC0000; color: white; padding: 8px;")
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

        btn_delete.clicked.connect(self._do_delete)
        btn_export.clicked.connect(self._do_export)
        btn_close.clicked.connect(self.reject)

    def _load_data(self):
        try:
            period = self.txt_period.text().strip()
            id_card = self.txt_id_card.text().strip()

            if self.is_network_mode:
                try:
                    from network.client import _request
                    params = {}
                    if period:
                        params['period'] = period
                    if id_card:
                        params['id_card'] = id_card
                    data = _request('GET', '/api/tekun_payment', params)
                    records = data.get('records', [])
                except Exception as e:
                    print(f"网络获取数据失败: {e}")
                    records = []
            else:
                from data.excel_importer import get_all_tekun_payments
                records = get_all_tekun_payments(period, id_card)

            self.table.setRowCount(len(records))
            for row_idx, p in enumerate(records):
                if isinstance(p, dict):
                    p_id = p.get('id', '')
                    p_period = p.get('period', '')
                    p_name = p.get('name', '')
                    p_id_card = p.get('id_card', '')
                    p_village = p.get('village', '')
                    p_bank_account = p.get('bank_account', '')
                    p_amount = p.get('amount', '')
                    p_payment_status = p.get('payment_status', '')
                    p_import_source = p.get('import_source', '')
                else:
                    p_id = p.id
                    p_period = getattr(p, 'period', '')
                    p_name = p.name
                    p_id_card = getattr(p, 'id_card', '')
                    p_village = getattr(p, 'village', '')
                    p_bank_account = p.bank_account
                    p_amount = p.amount
                    p_payment_status = getattr(p, 'payment_status', '')
                    p_import_source = getattr(p, 'import_source', '')

                item_name = QTableWidgetItem(p_name)
                item_name.setData(Qt.ItemDataRole.UserRole, p_id)
                self.table.setItem(row_idx, 0, QTableWidgetItem(p_period))
                self.table.setItem(row_idx, 1, item_name)
                self.table.setItem(row_idx, 2, QTableWidgetItem(p_id_card))
                self.table.setItem(row_idx, 3, QTableWidgetItem(p_village))
                self.table.setItem(row_idx, 4, QTableWidgetItem(p_bank_account))
                self.table.setItem(row_idx, 5, QTableWidgetItem(p_amount))
                self.table.setItem(row_idx, 6, QTableWidgetItem(p_payment_status))
                self.table.setItem(row_idx, 7, QTableWidgetItem(p_import_source))

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
                id_item = self.table.item(row, 1)
                if id_item:
                    row_ids.append(id_item.data(Qt.ItemDataRole.UserRole))

            if self.is_network_mode:
                from network.client import _request
                for rid in row_ids:
                    if rid:
                        _request('DELETE', f'/api/tekun_payment/{rid}')
            else:
                from data.excel_importer import delete_tekun_payment
                for rid in row_ids:
                    if rid:
                        delete_tekun_payment(rid)

            self._load_data()
            QMessageBox.information(self, "提示", "删除成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除失败：{e}")

    def _do_export(self):
        try:
            period = self.txt_period.text().strip()
            id_card = self.txt_id_card.text().strip()

            if self.is_network_mode:
                from network.client import _request
                params = {}
                if period:
                    params['period'] = period
                if id_card:
                    params['id_card'] = id_card
                data = _request('GET', '/api/tekun_payment', params)
                records = data.get('records', [])
            else:
                from data.excel_importer import get_all_tekun_payments
                records = get_all_tekun_payments(period, id_card)

            if not records:
                QMessageBox.warning(self, "提示", "没有数据可导出")
                return

            dis_map = {}
            if not self.is_network_mode:
                from core.database import get_session, Person
                _s = get_session()
                try:
                    dis_map = {pp.id_card: getattr(pp, 'dis_level', '') or ''
                               for pp in _s.query(Person).all() if pp.id_card}
                finally:
                    _s.close()

            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出Excel", f"特困_{datetime.now().strftime('%Y%m%d')}.xlsx",
                "Excel文件 (*.xlsx)"
            )
            if not file_path:
                return

            import pandas as pd
            data = []
            for p in records:
                if isinstance(p, dict):
                    data.append({
                        "费款所属期": p.get('period', ''),
                        "姓名": p.get('name', ''),
                        "身份证号": p.get('id_card', ''),
                        "残疾等级": p.get('dis_level', ''),
                        "所属乡镇": p.get('town', ''),
                        "所属村": p.get('village', ''),
                        "银行账号": p.get('bank_account', ''),
                        "金额": p.get('amount', ''),
                        "支付标志": p.get('payment_status', ''),
                        "导入来源": p.get('import_source', ''),
                    })
                else:
                    _id_card = getattr(p, 'id_card', '')
                    data.append({
                        "费款所属期": getattr(p, 'period', ''),
                        "姓名": p.name,
                        "身份证号": _id_card,
                        "残疾等级": dis_map.get(_id_card, ''),
                        "所属乡镇": getattr(p, 'town', ''),
                        "所属村": getattr(p, 'village', ''),
                        "银行账号": p.bank_account,
                        "金额": p.amount,
                        "支付标志": getattr(p, 'payment_status', ''),
                        "导入来源": getattr(p, 'import_source', ''),
                    })

            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            QMessageBox.information(self, "提示", f"导出成功！\n共 {len(records)} 条记录")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败：{e}")
