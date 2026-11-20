from .._imports import *
from .._consts import *
from ..funcs import *



class TekunViewDialogLoadDataMixin:
    def _load_data(self):
        try:
            period = self.txt_period.text().strip()
            id_card = self.txt_id_card.text().strip()

            if self.is_network_mode:
                try:
                    from network.client import _request
                    query = []
                    if period:
                        query.append(('period', period))
                    if id_card:
                        query.append(('id_card', id_card))
                    path = '/api/tekun_payment'
                    if query:
                        path += '?' + urlencode(query)
                    data = _request('GET', path)
                    records = data.get('records', []) or []
                except Exception as e:
                    self.lbl_count.setText("查询失败")
                    QMessageBox.critical(self, "错误", f"查询失败：{e}")
                    return
            else:
                from data.excel_importer import get_all_tekun_payments
                records = get_all_tekun_payments(period, id_card)

            self.table.setUpdatesEnabled(False)
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

            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            # 列宽按“表头 + 实际数据”取大计算；身份证号、银行账号等长号码列放宽上限
            fm = self.table.fontMetrics()
            wide_cols = {"身份证号", "银行账号", "卡号"}
            for col_idx, h in enumerate(self.headers):
                longest = fm.horizontalAdvance(h)
                for row in range(min(self.table.rowCount(), 200)):
                    item = self.table.item(row, col_idx)
                    if item is not None:
                        longest = max(longest, fm.horizontalAdvance(item.text()))
                cap = 300 if h in wide_cols else 200
                self.table.setColumnWidth(col_idx, min(max(longest + 26, 70), cap))
            self.table.setUpdatesEnabled(True)
            self.lbl_count.setText(f"共 {len(records)} 条")
        except Exception as e:
            self.table.setUpdatesEnabled(True)
            self.lbl_count.setText("查询失败")
            QMessageBox.critical(self, "错误", f"加载数据失败：{e}")
