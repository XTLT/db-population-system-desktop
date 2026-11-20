from .._imports import *
from .._consts import *
from ..funcs import *



class StudentQueryDialogGetSelectedPersonIdsMixin:
    def _get_selected_person_ids(self):
        selected = []
        for row in range(self.table.rowCount()):
            check_item = self.table.item(row, 0)
            if check_item and check_item.checkState() == Qt.CheckState.Checked:
                pid = check_item.data(Qt.ItemDataRole.UserRole)
                if pid:
                    selected.append(pid)
        return list(set(selected))
