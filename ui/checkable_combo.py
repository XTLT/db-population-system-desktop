from PyQt6.QtWidgets import (
    QWidget, QPushButton, QCheckBox, QScrollArea, QGridLayout, QVBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent


class CheckableComboBox(QWidget):
    selectionChanged = pyqtSignal()

    def __init__(self, items, parent=None):
        super().__init__(parent)
        self._items = items
        self._selected = []
        self._popup_visible = False

        self._btn = QPushButton("全部")
        self._btn.setStyleSheet(
            "QPushButton { text-align: left; padding: 4px 8px; border: 1px solid #ccc; "
            "background: white; } QPushButton:hover { border: 1px solid #999; }"
        )
        self._btn.setFixedHeight(28)
        self._btn.clicked.connect(self._toggle_popup)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._btn)

        self._popup = QWidget(self, Qt.WindowType.Popup)
        self._popup.setFixedWidth(220)
        popup_lay = QVBoxLayout(self._popup)
        popup_lay.setContentsMargins(4, 4, 4, 4)
        popup_lay.setSpacing(2)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(min(len(items) * 26 + 30, 180))
        container = QWidget()
        self._grid = QGridLayout(container)
        self._grid.setSpacing(2)
        self._grid.setContentsMargins(0, 0, 0, 0)

        self._suppress = False
        self._checkboxes = []

        cb_all = QCheckBox("全部")
        cb_all.setChecked(True)
        cb_all.stateChanged.connect(self._on_all_changed)
        self._grid.addWidget(cb_all, 0, 0)
        self._checkboxes.append(("全部", cb_all))

        cols = 2
        for idx, text in enumerate(items):
            cb = QCheckBox(text)
            cb.stateChanged.connect(self._on_item_changed)
            row = (idx + 1) // cols + 0
            col = (idx + 1) % cols
            self._grid.addWidget(cb, row, col)
            self._checkboxes.append((text, cb))

        scroll.setWidget(container)
        popup_lay.addWidget(scroll)

    def _toggle_popup(self):
        if self._popup_visible:
            self._popup.hide()
            self._popup_visible = False
        else:
            pos = self._btn.mapToGlobal(self._btn.rect().bottomLeft())
            self._popup.move(pos)
            self._popup.show()
            self._popup_visible = True

    def eventFilter(self, obj, event):
        if obj == self._popup and event.type() == QEvent.Type.MouseButtonPress:
            if not self._popup.geometry().contains(event.globalPosition().toPoint()):
                self._popup.hide()
                self._popup_visible = False
        return super().eventFilter(obj, event)

    def _on_all_changed(self, state):
        if self._suppress:
            return
        self._suppress = True
        checked = state == 2
        for text, cb in self._checkboxes:
            if text != "全部":
                cb.setChecked(checked)
        self._suppress = False
        self._update_button()
        self.selectionChanged.emit()

    def _on_item_changed(self, state):
        if self._suppress:
            return
        self._suppress = True
        all_checked = all(
            cb.isChecked() for text, cb in self._checkboxes if text != "全部"
        )
        self._checkboxes[0][1].setChecked(all_checked)
        self._suppress = False
        self._update_button()
        self.selectionChanged.emit()

    def _update_button(self):
        selected = self.get_selected()
        if not selected:
            self._btn.setText("全部")
        elif len(selected) <= 2:
            self._btn.setText("、".join(selected))
        else:
            self._btn.setText(f"{selected[0]}、{selected[1]}等{len(selected)}项")

    def get_selected(self):
        if self._checkboxes[0][1].isChecked():
            return []
        return [text for text, cb in self._checkboxes if text != "全部" and cb.isChecked()]

    def reset_selection(self):
        self._suppress = True
        self._checkboxes[0][1].setChecked(True)
        for text, cb in self._checkboxes:
            if text != "全部":
                cb.setChecked(False)
        self._suppress = False
        self._update_button()
