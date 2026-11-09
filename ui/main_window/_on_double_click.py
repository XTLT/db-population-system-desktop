from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt
from core.database import Person
from dialogs.person.edit_dialog import EditDialog


def _on_double_click(self, index):
    row = index.row()
    if row < 0:
        return

    # 主窗口表格由 _show_family 渲染：0=家庭人员姓名，1=身份证号码，2=与户主关系……
    # 人员标识优先取第 0 列 item 上存的 UserRole（真实 Person.id），
    # 取不到时回退到第 1 列的身份证号（服务端按身份证号也能定位）。
    name_item = self.table.item(row, 0)
    card_item = self.table.item(row, 1)
    if not name_item or not name_item.text():
        return
    if name_item.text().startswith("第") or name_item.text().startswith("匹配"):
        return

    pid = name_item.data(Qt.ItemDataRole.UserRole)
    if not pid and card_item:
        pid = card_item.text().strip()
    if not pid:
        QMessageBox.information(self, "提示", "该行没有可定位的人员标识，无法打开编辑窗口")
        return

    if self.is_network_mode:
        from network.client import api_person
        try:
            data = api_person(pid)
            person = type('Person', (), data)()
            person.id = data.get('id', pid)
            dialog = EditDialog(person, self)
            if dialog.exec():
                self._do_search()
        except ConnectionError as e:
            QMessageBox.critical(self, "连接错误", str(e))
    else:
        from core.database import get_session
        session = get_session()
        try:
            person = session.query(Person).filter(Person.id == pid).first()
            if not person and card_item and card_item.text().strip():
                person = session.query(Person).filter(
                    Person.id_card == card_item.text().strip()
                ).first()
            if person:
                dialog = EditDialog(person, self)
                if dialog.exec():
                    self._do_search()
        finally:
            session.close()
