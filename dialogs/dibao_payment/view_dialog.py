from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QLineEdit, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime

from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR


class DibaoViewDialog(QDialog):
    def __init__(self, is_network_mode: bool = False, is_admin: bool = False, parent=None):
        super().__init__(parent)
        self.is_network_mode = is_network_mode
        self.is_admin = is_admin
        self.setWindowTitle("低保数据")
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
        self.headers = ["费款所属期", "姓名", "身份证号", "村名称", "性别", "和申请人关系",
                   "共同生活家庭成员", "享受保障人口数", "家庭保障总金额", "家庭最低生活基本保障金",
                   "家庭特殊困难补助金", "家庭调剂金额", "特殊困难情形", "特殊困难补助金",
                   "初始享受时间", "始发年月", "导入来源"]
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
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
                    data = _request('GET', '/api/dibao_payment', params)
                    records = data.get('records', [])
                except Exception as e:
                    print(f"网络获取数据失败: {e}")
                    records = []
            else:
                from data.excel_importer import get_all_dibao_payments
                records = get_all_dibao_payments(period, id_card)

            self.table.setUpdatesEnabled(False)
            self.table.setRowCount(len(records))
            for row_idx, p in enumerate(records):
                if isinstance(p, dict):
                    p_id = p.get('id', '')
                    p_period = p.get('period', '')
                    p_name = p.get('name', '')
                    p_id_card = p.get('id_card', '')
                    p_village = p.get('village', '')
                    p_gender = p.get('gender', '')
                    p_relation = p.get('relation', '')
                    p_family_members = p.get('family_members', '')
                    p_family_count = p.get('family_count', '')
                    p_amount = p.get('amount', '')
                    p_base_amount = p.get('base_amount', '')
                    p_special_amount = p.get('special_amount', '')
                    p_adjust_amount = p.get('adjust_amount', '')
                    p_special_situation = p.get('special_situation', '')
                    p_special_subsidy = p.get('special_subsidy', '')
                    p_start_time = p.get('start_time', '')
                    p_issue_month = p.get('issue_month', '')
                    p_import_source = p.get('import_source', '')
                else:
                    p_id = p.id
                    p_period = getattr(p, 'period', '')
                    p_name = p.name
                    p_id_card = getattr(p, 'id_card', '')
                    p_village = getattr(p, 'village', '')
                    p_gender = getattr(p, 'gender', '')
                    p_relation = getattr(p, 'relation', '')
                    p_family_members = getattr(p, 'family_members', '')
                    p_family_count = getattr(p, 'family_count', '')
                    p_amount = p.amount
                    p_base_amount = getattr(p, 'base_amount', '')
                    p_special_amount = getattr(p, 'special_amount', '')
                    p_adjust_amount = getattr(p, 'adjust_amount', '')
                    p_special_situation = getattr(p, 'special_situation', '')
                    p_special_subsidy = getattr(p, 'special_subsidy', '')
                    p_start_time = getattr(p, 'start_time', '')
                    p_issue_month = getattr(p, 'issue_month', '')
                    p_import_source = getattr(p, 'import_source', '')

                item_name = QTableWidgetItem(p_name)
                item_name.setData(Qt.ItemDataRole.UserRole, p_id)
                values = [p_period, p_name, p_id_card, p_village, p_gender, p_relation,
                          p_family_members, p_family_count, p_amount, p_base_amount,
                          p_special_amount, p_adjust_amount, p_special_situation,
                          p_special_subsidy, p_start_time, p_issue_month, p_import_source]
                for col, val in enumerate(values):
                    if col == 1:
                        self.table.setItem(row_idx, col, item_name)
                    else:
                        self.table.setItem(row_idx, col, QTableWidgetItem(val))

            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            for col_idx, h in enumerate(self.headers):
                self.table.setColumnWidth(col_idx, min(max(len(h) * 18 + 30, 70), 200))
            self.table.setUpdatesEnabled(True)
        except Exception as e:
            self.table.setUpdatesEnabled(True)
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
                        _request('DELETE', f'/api/dibao_payment/{rid}')
            else:
                from data.excel_importer import delete_dibao_payment
                for rid in row_ids:
                    if rid:
                        delete_dibao_payment(rid)

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
                data = _request('GET', '/api/dibao_payment', params)
                records = data.get('records', [])
            else:
                from data.excel_importer import get_all_dibao_payments
                records = get_all_dibao_payments(period, id_card)

            if not records:
                QMessageBox.warning(self, "提示", "没有数据可导出")
                return

            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出Excel", f"低保_{datetime.now().strftime('%Y%m%d')}.xlsx",
                "Excel文件 (*.xlsx)"
            )
            if not file_path:
                return

            import pandas as pd
            data = []
            for p in records:
                if isinstance(p, dict):
                    data.append({
                        "村名称": p.get('village', ''),
                        "救助类型": "低保",
                        "人员姓名": p.get('name', ''),
                        "人员身份证号": p.get('id_card', ''),
                        "性别": p.get('gender', ''),
                        "和申请人关系": p.get('relation', ''),
                        "共同生活家庭成员": p.get('family_members', ''),
                        "享受保障人口数": p.get('family_count', ''),
                        "家庭保障总金额": p.get('amount', ''),
                        "家庭最低生活基本保障金": p.get('base_amount', ''),
                        "家庭特殊困难补助金": p.get('special_amount', ''),
                        "家庭调剂金额": p.get('adjust_amount', ''),
                        "特殊困难情形（分类施保）": p.get('special_situation', ''),
                        "特殊困难补助金": p.get('special_subsidy', ''),
                        "初始享受时间": p.get('start_time', ''),
                        "始发年月": p.get('issue_month', '') or p.get('period', ''),
                        "费款所属期": p.get('period', ''),
                        "导入来源": p.get('import_source', ''),
                    })
                else:
                    data.append({
                        "村名称": getattr(p, 'village', ''),
                        "救助类型": "低保",
                        "人员姓名": p.name,
                        "人员身份证号": getattr(p, 'id_card', ''),
                        "性别": getattr(p, 'gender', ''),
                        "和申请人关系": getattr(p, 'relation', ''),
                        "共同生活家庭成员": getattr(p, 'family_members', ''),
                        "享受保障人口数": getattr(p, 'family_count', ''),
                        "家庭保障总金额": p.amount,
                        "家庭最低生活基本保障金": getattr(p, 'base_amount', ''),
                        "家庭特殊困难补助金": getattr(p, 'special_amount', ''),
                        "家庭调剂金额": getattr(p, 'adjust_amount', ''),
                        "特殊困难情形（分类施保）": getattr(p, 'special_situation', ''),
                        "特殊困难补助金": getattr(p, 'special_subsidy', ''),
                        "初始享受时间": getattr(p, 'start_time', ''),
                        "始发年月": getattr(p, 'issue_month', '') or getattr(p, 'period', ''),
                        "费款所属期": getattr(p, 'period', ''),
                        "导入来源": getattr(p, 'import_source', ''),
                    })

            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            from data.excel_importer import _auto_fit_columns
            _auto_fit_columns(file_path)
            QMessageBox.information(self, "提示", f"导出成功！\n共 {len(records)} 条记录")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败：{e}")
