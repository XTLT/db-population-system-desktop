from PyQt6.QtWidgets import QMessageBox
from core.database import search_by_name


def _do_search(self):
    name = self.txt_search.text().strip()
    if not name:
        return
    self.current_name = name
    if self.is_network_mode:
        from network.client import api_search
        try:
            results = api_search(name)
            self.matches = [type('Person', (), r)() for r in results]
        except ConnectionError as e:
            QMessageBox.critical(self, "连接错误", str(e))
            return
    else:
        self.matches = search_by_name(name)
    self._display_name_list()
