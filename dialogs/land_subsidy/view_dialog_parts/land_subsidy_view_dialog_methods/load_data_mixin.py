from .._imports import *
from .._consts import *
from ..funcs import *



class LandSubsidyViewDialogLoadDataMixin:
    def _load_data(self):
        try:
            year = self.cmb_year.currentText() if self.cmb_year.currentText() != "全部" else None
            search = self.txt_search.text().strip()

            if self.is_network_mode:
                try:
                    import urllib.parse
                    from network.client import _request
                    url = '/api/land_subsidy'
                    params = []
                    if year:
                        params.append(f'year={urllib.parse.quote(year)}')
                    if search:
                        params.append(f'search={urllib.parse.quote(search)}')
                    if params:
                        url += '?' + '&'.join(params)
                    data = _request('GET', url)
                    subsidies = data.get('subsidies', [])
                except Exception as e:
                    print(f"网络获取数据失败: {e}")
                    subsidies = []
            else:
                from data.excel_importer import get_all_land_subsidies
                subsidies = get_all_land_subsidies(year)
                if self.filter_id_card:
                    subsidies = [s for s in subsidies if s.id_card == self.filter_id_card]
                elif search:
                    subsidies = [s for s in subsidies if search in s.name]

            self.table.setUpdatesEnabled(False)
            self.table.setRowCount(len(subsidies))
            for row_idx, s in enumerate(subsidies):
                if isinstance(s, dict):
                    values = [str(row_idx + 1), s.get('year', '') or s.get('subsidy_year', ''),
                             s.get('name', ''), s.get('id_card', ''),
                             s.get('phone', ''), s.get('bank_account', ''), s.get('bank_name', ''),
                             s.get('total_amount', ''), s.get('land_time', ''),
                             s.get('certified_area', ''), s.get('base_standard', ''),
                             s.get('rape_area', ''), s.get('rape_standard', ''), s.get('rape_amount', '')]
                    item_id = s.get('id', '')
                else:
                    values = [str(row_idx + 1), s.subsidy_year, s.name, s.id_card,
                             getattr(s, 'phone', ''), getattr(s, 'bank_account', ''), getattr(s, 'bank_name', ''),
                             s.total_amount, getattr(s, 'land_time', ''),
                             s.certified_area, s.base_standard, s.rape_area, getattr(s, 'rape_standard', ''), s.rape_amount]
                    item_id = s.id
                for col_idx, val in enumerate(values):
                    item = QTableWidgetItem(str(val) if val else "")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setData(Qt.ItemDataRole.UserRole, item_id)
                    self.table.setItem(row_idx, col_idx, item)

            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            self.table.horizontalHeader().setStretchLastSection(True)
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
        except Exception as e:
            self.table.setUpdatesEnabled(True)
            print(f"加载数据失败: {e}")
