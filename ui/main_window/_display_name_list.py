from PyQt6.QtWidgets import QScrollArea, QWidget, QGridLayout, QPushButton
from PyQt6.QtGui import QFont
from core.config import FONT_NAME, MATCHES_PER_COLUMN


def _display_name_list(self):
    for i in reversed(range(self.name_layout.count())):
        widget = self.name_layout.itemAt(i).widget()
        if widget and widget != self.name_label:
            widget.deleteLater()

    self.table.setRowCount(0)
    self.table.setColumnCount(0)

    if not self.matches:
        self.name_label.setText("未找到该人员")
        self.name_label.setStyleSheet("color: red; font-weight: bold; background-color: #DDEBF7; padding: 8px; border: 1px solid #4472C4;")
        return

    count = len(self.matches)
    self.name_label.setText(f"共找到 {count} 个同名同姓人员（点击姓名查看所有同名人员信息）")
    self.name_label.setStyleSheet("color: #003366; font-weight: bold; background-color: #DDEBF7; padding: 8px; border: 1px solid #4472C4;")

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll_widget = QWidget()
    grid_layout = QGridLayout(scroll_widget)
    grid_layout.setSpacing(4)
    grid_layout.setContentsMargins(8, 8, 8, 8)

    for idx, person in enumerate(self.matches):
        col = idx // MATCHES_PER_COLUMN
        row = idx % MATCHES_PER_COLUMN
        btn = QPushButton(person.name)
        btn.setFont(QFont(FONT_NAME, 14, QFont.Weight.Bold))
        if person.is_migrated == "是":
            btn.setStyleSheet("background-color: #FFFFCC; padding: 6px; border: 1px solid #ccc; color: #CC0000; text-decoration: line-through;")
        else:
            btn.setStyleSheet("background-color: #FFFFCC; padding: 6px; border: 1px solid #ccc;")
        btn.setFixedHeight(36)
        btn.setMinimumWidth(120)
        btn.clicked.connect(lambda checked, p=person: self._show_family(p))
        grid_layout.addWidget(btn, row, col)

    scroll.setWidget(scroll_widget)
    self.name_layout.addWidget(scroll)
