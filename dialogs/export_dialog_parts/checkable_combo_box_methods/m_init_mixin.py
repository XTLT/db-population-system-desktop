from .._imports import *
from .._consts import *
from ..funcs import *



class CheckableComboBoxMInitMixin:
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
