from .._imports import *
from .._consts import *
from ..funcs import *



class DibaoViewDialogLoadDataMixin:
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
                    path = '/api/dibao_payment'
                    if query:
                        path += '?' + urlencode(query)
                    data = _request('GET', path)
                    records = data.get('records', []) or []
                except Exception as e:
                    self.lbl_count.setText("查询失败")
                    QMessageBox.critical(self, "错误", f"查询失败：{e}")
                    return
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
                    p_bank_account = p.get('bank_account', '')
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
                    p_bank_account = getattr(p, 'bank_account', '')

                item_name = QTableWidgetItem(p_name)
                item_name.setData(Qt.ItemDataRole.UserRole, p_id)
                values = [p_period, p_name, p_id_card, p_village, p_gender, p_relation,
                          p_family_members, p_family_count, p_amount, p_base_amount,
                          p_special_amount, p_adjust_amount, p_special_situation,
                          p_special_subsidy, p_start_time, p_issue_month, p_import_source,
                          p_bank_account]
                for col, val in enumerate(values):
                    if col == 1:
                        self.table.setItem(row_idx, col, item_name)
                    else:
                        self.table.setItem(row_idx, col, QTableWidgetItem(val))

            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            # 列宽按“表头 + 实际数据”取大计算；身份证号、银行账号等长号码列放宽上限
            fm = self.table.fontMetrics()
            wide_cols = {"身份证号", "银行账号"}
            for col_idx, h in enumerate(self.headers):
                longest = fm.horizontalAdvance(h)
                for row in range(min(self.table.rowCount(), 200)):
                    it = self.table.item(row, col_idx)
                    if it is not None:
                        longest = max(longest, fm.horizontalAdvance(it.text()))
                cap = 300 if h in wide_cols else 200
                self.table.setColumnWidth(col_idx, min(max(longest + 26, 70), cap))
            self.table.setUpdatesEnabled(True)
            self.lbl_count.setText(f"共 {len(records)} 条")
        except Exception as e:
            self.table.setUpdatesEnabled(True)
            self.lbl_count.setText("查询失败")
            QMessageBox.critical(self, "错误", f"加载数据失败：{e}")
