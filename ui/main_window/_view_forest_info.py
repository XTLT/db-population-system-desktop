from PyQt6.QtWidgets import QDialog, QLabel, QMessageBox, QTableWidget, QVBoxLayout, QTableWidgetItem, QHeaderView
from core.database import Person


def _view_forest_info(self):
    from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
    dialog = QDialog(self)
    dialog.setWindowTitle("林地信息查看")
    dialog.resize(900, 500)
    layout = QVBoxLayout(dialog)

    headers = ["户号", "姓名", "地方公益林(亩)", "国家公益林(亩)", "非国有天然商品林(亩)"]
    table = QTableWidget()
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    layout.addWidget(table)

    persons = []
    if self.is_network_mode:
        try:
            from network.client import _request
            resp = _request('GET', '/api/persons?page=1&per_page=10000')
            persons = resp.get('persons', resp.get('data', resp.get('items', [])))
        except Exception as e:
            QMessageBox.warning(self, "错误", f"查询失败：{e}")
            return
    else:
        from core.database import get_session, Person
        session = get_session()
        persons = session.query(Person).all()
        session.close()

    rows = 0
    for p in persons:
        def _get(key, default=""):
            if isinstance(p, dict):
                return p.get(key) or default
            return getattr(p, key, None) or default
        lw = _get('local_welfare_forest_area')
        nw = _get('national_welfare_forest_area')
        cf = _get('commercial_forest_area')
        if lw or nw or cf:
            table.insertRow(rows)
            table.setItem(rows, 0, QTableWidgetItem(str(_get('hu_hao'))))
            table.setItem(rows, 1, QTableWidgetItem(str(_get('name'))))
            table.setItem(rows, 2, QTableWidgetItem(str(lw)))
            table.setItem(rows, 3, QTableWidgetItem(str(nw)))
            table.setItem(rows, 4, QTableWidgetItem(str(cf)))
            rows += 1

    lbl_summary = QLabel(f"共 {rows} 人有林地信息")
    layout.addWidget(lbl_summary)
    dialog.exec()
