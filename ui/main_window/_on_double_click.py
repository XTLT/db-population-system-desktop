from PyQt6.QtWidgets import QMessageBox
from core.database import Person
from dialogs.person.edit_dialog import EditDialog


def _on_double_click(self, index):
    row = index.row()
    if row < 0:
        return
    name_item = self.table.item(row, 1)
    id_item = self.table.item(row, 2)
    if not name_item or not id_item:
        return
    if not name_item.text() or name_item.text().startswith("第") or name_item.text().startswith("匹配"):
        return
    if self.is_network_mode:
        from network.client import api_person
        try:
            data = api_person(id_item.text())
            person = type('Person', (), data)()
            person.id = data['id']
            dialog = EditDialog(person, self)
            if dialog.exec():
                self._do_search()
        except ConnectionError as e:
            QMessageBox.critical(self, "连接错误", str(e))
    else:
        from core.database import get_session
        session = get_session()
        try:
            person = session.query(Person).filter(
                Person.name == name_item.text(),
                Person.id_card == id_item.text()
            ).first()
            if person:
                dialog = EditDialog(person, self)
                if dialog.exec():
                    self._do_search()
        finally:
            session.close()
