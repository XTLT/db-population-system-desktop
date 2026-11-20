from .._imports import *
from .._consts import *
from ..funcs import *

FIELD_OPTIONS = None
MATCH_BY_ID_CARD = None
MATCH_BY_NAME = None
_col_letter = None

class ColumnMappingDialogOnHeaderRowChangedMixin:
    def _on_header_row_changed(self):
        header_row = self.spin_header_row.value()
        self._headers = []
        max_col = self._ws.max_column
        for col in range(1, max_col + 1):
            val = self._ws.cell(header_row, col).value
            self._headers.append(str(val).strip() if val is not None else "")

        self.cbo_match_col.blockSignals(True)
        self.cbo_match_col.clear()
        for i, h in enumerate(self._headers):
            letter = _col_letter(i + 1)
            display = f"{letter}: {h or '(空)'}"
            self.cbo_match_col.addItem(display, i + 1)
        self.cbo_match_col.blockSignals(False)

        self.table.setRowCount(len(self._headers))
        self._field_combos = []

        for i, h in enumerate(self._headers):
            letter = _col_letter(i + 1)
            idx_item = QTableWidgetItem(letter)
            idx_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, idx_item)

            header_item = QTableWidgetItem(h or "(空)")
            header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 1, header_item)

            combo = QComboBox()
            combo.setFont(QFont(FONT_NAME, FONT_SIZE))
            for val, label in FIELD_OPTIONS:
                combo.addItem(label, val)
            self._field_combos.append(combo)
            self.table.setCellWidget(i, 2, combo)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._update_field_combos()
