from .._imports import *
from .._consts import *
from ..funcs import *


class HouseBuildEditDialogSetupApprovalTabMixin:
    def _setup_approval_tab(self):
        outer = QVBoxLayout(self.tab_approval)
        outer.setContentsMargins(6, 6, 6, 6)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setSpacing(8)
        font = QFont(FONT_NAME, FONT_SIZE)

        box_head = QGroupBox("审批基本情况（面积单位：平方米）")
        grid = QGridLayout(box_head)
        self.e_ap_land_area = QLineEdit()
        self.e_ap_foundation = QLineEdit()
        self.e_ap_address = QLineEdit()
        self.e_ap_floor_area = QLineEdit()
        self.e_ap_floors = QLineEdit()
        self.e_ap_height = QLineEdit()
        self.cmb_ap_build_type = QComboBox()
        self.cmb_ap_land_type = QComboBox()
        for value, text in BUILD_TYPE_OPTIONS:
            self.cmb_ap_build_type.addItem(text, value)
        for value, text in LAND_TYPE_OPTIONS:
            self.cmb_ap_land_type.addItem(text, value)
        for w in (self.e_ap_land_area, self.e_ap_foundation, self.e_ap_address,
                  self.e_ap_floor_area, self.e_ap_floors, self.e_ap_height):
            w.setFont(font)
        self.cmb_ap_build_type.setFont(font)
        self.cmb_ap_land_type.setFont(font)

        grid.addWidget(self._lbl("批准宅基地面积"), 0, 0)
        grid.addWidget(self.e_ap_land_area, 0, 1)
        grid.addWidget(self._lbl("房基占地面积"), 0, 2)
        grid.addWidget(self.e_ap_foundation, 0, 3)
        grid.addWidget(self._lbl("建房地址"), 0, 4)
        grid.addWidget(self.e_ap_address, 0, 5)
        grid.addWidget(self._lbl("建房类型"), 1, 0)
        grid.addWidget(self.cmb_ap_build_type, 1, 1)
        grid.addWidget(self._lbl("地类"), 1, 2)
        grid.addWidget(self.cmb_ap_land_type, 1, 3)
        grid.addWidget(self._lbl("住房建筑面积"), 1, 4)
        grid.addWidget(self.e_ap_floor_area, 1, 5)
        grid.addWidget(self._lbl("建筑层数"), 2, 0)
        grid.addWidget(self.e_ap_floors, 2, 1)
        grid.addWidget(self._lbl("建筑高度"), 2, 2)
        grid.addWidget(self.e_ap_height, 2, 3)
        layout.addWidget(box_head)

        self.ap_widgets = {}
        for key, title in APPROVAL_GROUPS:
            box = QGroupBox(title)
            grid_b = QGridLayout(box)
            opinion = QTextEdit()
            opinion.setFont(font)
            opinion.setFixedHeight(64)
            leader = QLineEdit()
            leader.setFont(font)
            date = QLineEdit()
            date.setFont(font)
            date.setPlaceholderText("如 2026年11月20日")
            grid_b.addWidget(opinion, 0, 0, 1, 6)
            grid_b.addWidget(self._lbl("负责人"), 1, 0)
            grid_b.addWidget(leader, 1, 1, 1, 2)
            grid_b.addWidget(self._lbl("日期"), 1, 3)
            grid_b.addWidget(date, 1, 4, 1, 2)
            layout.addWidget(box)
            self.ap_widgets[key] = {'opinion': opinion, 'leader': leader, 'date': date}

        layout.addStretch()
        scroll.setWidget(inner)
        outer.addWidget(scroll)

    def _lbl(self, text):
        label = QLabel(text)
        label.setFont(QFont(FONT_NAME, FONT_SIZE))
        return label
