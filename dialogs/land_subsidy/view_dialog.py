from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QComboBox, QLineEdit, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime

from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR


class LandSubsidyViewDialog(QDialog):
    def __init__(self, is_network_mode: bool = False, is_admin: bool = False, parent=None):
        super().__init__(parent)
        self.is_network_mode = is_network_mode
        self.is_admin = is_admin
        self.filter_id_card = None
        self.setWindowTitle("地力补贴数据")
        self.setFixedSize(1000, 600)
        self._setup_ui()
        try:
            self._load_years()
            self._load_data()
        except Exception as e:
            QMessageBox.warning(self, "提示", f"加载数据时出错：{e}")

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()
        lbl_year = QLabel("补贴年度：")
        lbl_year.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.cmb_year = QComboBox()
        self.cmb_year.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.cmb_year.addItem("全部")
        filter_layout.addWidget(lbl_year)
        filter_layout.addWidget(self.cmb_year)

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
        headers = ["补贴年度", "姓名", "身份证号", "残疾等级", "确权颁发面积", "补贴面积(亩)", "基础补贴标准(元/亩)",
                   "油菜面积(亩)", "油菜金额(元)", "补贴总金额(元)", "导入时间"]
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

        self.cmb_year.currentTextChanged.connect(lambda: self._load_data())
        self.txt_search.textChanged.connect(lambda: self._load_data())
        btn_delete.clicked.connect(self._do_delete)
        btn_export.clicked.connect(self._do_export)
        btn_close.clicked.connect(self.reject)

    def _load_years(self):
        try:
            if self.is_network_mode:
                try:
                    from network.client import _request
                    data = _request('GET', '/api/land_subsidy/years')
                    years = data.get('years', [])
                except Exception as e:
                    print(f"网络获取年度失败: {e}")
                    years = []
            else:
                from data.excel_importer import get_all_land_subsidies
                all_data = get_all_land_subsidies()
                years = list(set(s.subsidy_year for s in all_data if s.subsidy_year))
                years.sort(reverse=True)

            self.cmb_year.clear()
            self.cmb_year.addItem("全部")
            for y in years:
                self.cmb_year.addItem(y)
        except Exception as e:
            print(f"加载年度失败: {e}")

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

            dis_map = {}
            if not self.is_network_mode:
                from core.database import get_session, Person
                _s = get_session()
                try:
                    dis_map = {pp.id_card: getattr(pp, 'dis_level', '') or ''
                               for pp in _s.query(Person).all() if pp.id_card}
                finally:
                    _s.close()

            self.table.setRowCount(len(subsidies))
            for row_idx, s in enumerate(subsidies):
                if isinstance(s, dict):
                    values = [s.get('subsidy_year', ''), s.get('name', ''), s.get('id_card', ''),
                             s.get('dis_level', ''),
                             s.get('certified_area', ''), s.get('subsidy_area', ''),
                             s.get('base_standard', ''), s.get('rape_area', ''),
                             s.get('rape_amount', ''), s.get('total_amount', ''),
                             s.get('import_time', '')]
                    item_id = s.get('id', '')
                else:
                    values = [s.subsidy_year, s.name, s.id_card,
                             dis_map.get(s.id_card, ''),
                             s.certified_area, s.subsidy_area,
                             s.base_standard, s.rape_area, s.rape_amount, s.total_amount, s.import_time]
                    item_id = s.id
                for col_idx, val in enumerate(values):
                    item = QTableWidgetItem(str(val) if val else "")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setData(Qt.ItemDataRole.UserRole, item_id)
                    self.table.setItem(row_idx, col_idx, item)

            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            self.table.horizontalHeader().setStretchLastSection(True)
        except Exception as e:
            print(f"加载数据失败: {e}")

    def _do_delete(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "提示", "请选择要删除的记录")
            return
        row = selected[0].row()
        subsidy_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除这条记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.is_network_mode:
                try:
                    from network.client import _request
                    _request('DELETE', f'/api/land_subsidy/{subsidy_id}')
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"删除失败：{e}")
                    return
            else:
                from data.excel_importer import delete_land_subsidy
                delete_land_subsidy(subsidy_id)
            self._load_data()

    def _do_export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "导出地力补贴", f"地力补贴_{datetime.now().strftime('%Y%m%d')}.xlsx",
            "Excel文件 (*.xlsx)"
        )
        if not path:
            return

        import pandas as pd
        data = []
        headers = ["补贴年度", "姓名", "身份证号", "残疾等级", "确权颁发面积", "补贴面积(亩)", "基础补贴标准(元/亩)",
                   "油菜面积(亩)", "油菜金额(元)", "补贴总金额(元)", "导入时间"]
        for row in range(self.table.rowCount()):
            row_data = {}
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data[headers[col]] = item.text() if item else ""
            data.append(row_data)
        df = pd.DataFrame(data)
        df.to_excel(path, index=False, engine="openpyxl")
        QMessageBox.information(self, "成功", f"数据已导出到：\n{path}")
