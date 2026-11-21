"""编辑对话框用到的取/填值小工具。"""

from PyQt6.QtWidgets import QComboBox, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidgetItem


def combo_set(combo: QComboBox, value):
    """按 data 选中；找不到就选第一项。"""
    idx = combo.findData(value or '')
    combo.setCurrentIndex(idx if idx >= 0 else 0)


def text_of(combo: QComboBox):
    return combo.currentData() or ''


def edit_text(line: QLineEdit):
    return line.text().strip()


def member_rows(table):
    """读取成员表非空行。"""
    rows = []
    for row in range(table.rowCount()):
        values = []
        for col in range(table.columnCount()):
            item = table.item(row, col)
            values.append((item.text() if item else '').strip())
        if values[0] or values[3]:
            rows.append({
                'seq': str(len(rows) + 1),
                'name': values[0], 'age': values[1], 'relation': values[2],
                'id_card': values[3], 'hukou': values[4],
            })
    return rows


def fill_member_rows(table, members):
    table.setRowCount(max(5, len(members)))
    for row in range(table.rowCount()):
        member = members[row] if row < len(members) else {}
        values = [member.get('name', ''), member.get('age', ''), member.get('relation', ''),
                  member.get('id_card', ''), member.get('hukou', '')]
        for col, text in enumerate(values):
            item = QTableWidgetItem(str(text))
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(row, col, item)
