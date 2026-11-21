from .._imports import *
from .._consts import *
from ..funcs import *


class HouseBuildEditDialogSetupApplyTabMixin:
    def _setup_apply_tab(self):
        outer = QVBoxLayout(self.tab_apply)
        outer.setContentsMargins(6, 6, 6, 6)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setSpacing(8)

        font = QFont(FONT_NAME, FONT_SIZE)

        # ---- 申请人信息 ----
        box_owner = QGroupBox("申请人信息")
        grid = QGridLayout(box_owner)
        self.e_owner_name = QLineEdit()
        self.e_owner_age = QLineEdit()
        self.e_owner_phone = QLineEdit()
        self.e_owner_hukou = QLineEdit()
        self.e_hu_hao = QLineEdit()
        self.e_hu_hao.setReadOnly(True)
        self.e_group_name = QLineEdit()
        self.cmb_gender = QComboBox()
        for value, text in GENDER_OPTIONS:
            self.cmb_gender.addItem(text, value)
        for w in (self.e_owner_name, self.e_owner_age, self.e_owner_phone, self.e_owner_hukou,
                  self.e_hu_hao, self.e_group_name):
            w.setFont(font)
        self.cmb_gender.setFont(font)

        grid.addWidget(self._lbl("姓名"), 0, 0)
        grid.addWidget(self.e_owner_name, 0, 1)
        grid.addWidget(self._lbl("性别"), 0, 2)
        grid.addWidget(self.cmb_gender, 0, 3)
        grid.addWidget(self._lbl("年龄"), 0, 4)
        grid.addWidget(self.e_owner_age, 0, 5)
        grid.addWidget(self._lbl("联系电话"), 1, 0)
        grid.addWidget(self.e_owner_phone, 1, 1)
        grid.addWidget(self._lbl("户号"), 1, 2)
        grid.addWidget(self.e_hu_hao, 1, 3)
        grid.addWidget(self._lbl("小组"), 1, 4)
        grid.addWidget(self.e_group_name, 1, 5)
        grid.addWidget(self._lbl("户口所在地"), 2, 0)
        grid.addWidget(self.e_owner_hukou, 2, 1, 1, 5)
        layout.addWidget(box_owner)

        # ---- 家庭成员 ----
        box_members = QGroupBox("家庭成员（本表最多打印 5 人，按户内成员顺序）")
        vbox_m = QVBoxLayout(box_members)
        self.tbl_members = QTableWidget()
        self.tbl_members.setFont(font)
        self.tbl_members.setRowCount(5)
        self.tbl_members.setColumnCount(len(MEMBER_HEADERS))
        self.tbl_members.setHorizontalHeaderLabels(MEMBER_HEADERS)
        self.tbl_members.verticalHeader().setVisible(True)
        self.tbl_members.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_members.setFixedHeight(190)
        vbox_m.addWidget(self.tbl_members)
        layout.addWidget(box_members)

        # ---- 拟建房情况 ----
        box_apply = QGroupBox("拟申请建房情况（面积单位：m²）")
        grid2 = QGridLayout(box_apply)
        self.e_apply_land_area = QLineEdit()
        self.e_building_area = QLineEdit()
        self.e_cert_no = QLineEdit()
        self.e_current_land_area = QLineEdit()
        self.e_disposal_other = QLineEdit()
        self.e_foundation_area = QLineEdit()
        self.e_east = QLineEdit()
        self.e_south = QLineEdit()
        self.e_west = QLineEdit()
        self.e_north = QLineEdit()
        self.e_house_floor_area = QLineEdit()
        self.e_floors = QLineEdit()
        self.e_building_height = QLineEdit()
        self.cmb_disposal = QComboBox()
        self.cmb_build_type = QComboBox()
        self.cmb_land_type = QComboBox()
        self.cmb_neighbor = QComboBox()
        self.cmb_design = QComboBox()
        for value, text in DISPOSAL_OPTIONS:
            self.cmb_disposal.addItem(text, value)
        for value, text in BUILD_TYPE_OPTIONS:
            self.cmb_build_type.addItem(text, value)
        for value, text in LAND_TYPE_OPTIONS:
            self.cmb_land_type.addItem(text, value)
        for value, text in YES_NO_OPTIONS:
            self.cmb_neighbor.addItem(text, value)
            self.cmb_design.addItem(text, value)
        for w in (self.e_apply_land_area, self.e_building_area, self.e_cert_no, self.e_current_land_area,
                  self.e_disposal_other, self.e_foundation_area, self.e_east, self.e_south,
                  self.e_west, self.e_north, self.e_house_floor_area, self.e_floors,
                  self.e_building_height):
            w.setFont(font)
        for combo in (self.cmb_disposal, self.cmb_build_type, self.cmb_land_type,
                      self.cmb_neighbor, self.cmb_design):
            combo.setFont(font)

        grid2.addWidget(self._lbl("申请宅基地面积"), 0, 0)
        grid2.addWidget(self._area_input(self.e_apply_land_area), 0, 1)
        grid2.addWidget(self._lbl("建筑面积"), 0, 2)
        grid2.addWidget(self._area_input(self.e_building_area), 0, 3)
        grid2.addWidget(self._lbl("权属证书号"), 0, 4)
        grid2.addWidget(self.e_cert_no, 0, 5)
        grid2.addWidget(self._lbl("现宅基地处置"), 1, 0)
        grid2.addWidget(self.cmb_disposal, 1, 1)
        grid2.addWidget(self._lbl("其他说明"), 1, 2)
        grid2.addWidget(self.e_disposal_other, 1, 3)
        grid2.addWidget(self._lbl("原宅基地面积"), 1, 4)
        grid2.addWidget(self._area_input(self.e_current_land_area), 1, 5)
        grid2.addWidget(self._lbl("房基占地面积"), 2, 0)
        grid2.addWidget(self._area_input(self.e_foundation_area), 2, 1)
        grid2.addWidget(self._lbl("建房类型"), 2, 2)
        grid2.addWidget(self.cmb_build_type, 2, 3)
        grid2.addWidget(self._lbl("地类"), 2, 4)
        grid2.addWidget(self.cmb_land_type, 2, 5)
        grid2.addWidget(self._lbl("东至"), 3, 0)
        grid2.addWidget(self.e_east, 3, 1)
        grid2.addWidget(self._lbl("南至"), 3, 2)
        grid2.addWidget(self.e_south, 3, 3)
        grid2.addWidget(self._lbl("西至"), 3, 4)
        grid2.addWidget(self.e_west, 3, 5)
        grid2.addWidget(self._lbl("北至"), 4, 0)
        grid2.addWidget(self.e_north, 4, 1)
        grid2.addWidget(self._lbl("住房建筑面积"), 4, 2)
        grid2.addWidget(self._area_input(self.e_house_floor_area), 4, 3)
        grid2.addWidget(self._lbl("建筑层数"), 4, 4)
        grid2.addWidget(self.e_floors, 4, 5)
        grid2.addWidget(self._lbl("建筑高度"), 5, 0)
        grid2.addWidget(self.e_building_height, 5, 1)
        grid2.addWidget(self._lbl("征求相邻权利人意见"), 5, 2)
        grid2.addWidget(self.cmb_neighbor, 5, 3)
        grid2.addWidget(self._lbl("是否有设计方案/通用图集"), 5, 4)
        grid2.addWidget(self.cmb_design, 5, 5)
        layout.addWidget(box_apply)

        # ---- 申请理由 ----
        box_reason = QGroupBox("申请理由（打印时姓名、日期留空，由申请人手写签名）")
        vbox_r = QVBoxLayout(box_reason)
        self.e_apply_reason = QTextEdit()
        self.e_apply_reason.setFont(font)
        self.e_apply_reason.setFixedHeight(80)
        vbox_r.addWidget(self.e_apply_reason)
        layout.addWidget(box_reason)

        # ---- 村（组）意见 ----
        box_village = QGroupBox("村（组）意见（打印时负责人、日期留空，由村委会盖章手写）")
        grid3 = QGridLayout(box_village)
        self.e_village_opinion = QTextEdit()
        self.e_village_opinion.setFont(font)
        self.e_village_opinion.setFixedHeight(70)
        self.e_village_leader = QLineEdit()
        self.e_village_leader.setFont(font)
        self.e_village_date = QLineEdit()
        self.e_village_date.setFont(font)
        self.e_village_date.setPlaceholderText("如 2026年11月20日")
        grid3.addWidget(self.e_village_opinion, 0, 0, 1, 6)
        grid3.addWidget(self._lbl("负责人（仅存档）"), 1, 0)
        grid3.addWidget(self.e_village_leader, 1, 1, 1, 2)
        grid3.addWidget(self._lbl("日期（仅存档）"), 1, 3)
        grid3.addWidget(self.e_village_date, 1, 4, 1, 2)
        layout.addWidget(box_village)

        layout.addStretch()
        scroll.setWidget(inner)
        outer.addWidget(scroll)

    def _area_input(self, edit):
        """面积输入框：右侧固定 m² 单位。"""
        box = QWidget()
        hbox = QHBoxLayout(box)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(4)
        hbox.addWidget(edit, 1)
        unit = QLabel("m²")
        unit.setFont(QFont(FONT_NAME, FONT_SIZE))
        hbox.addWidget(unit, 0)
        return box

    def _lbl(self, text):
        label = QLabel(text)
        label.setFont(QFont(FONT_NAME, FONT_SIZE))
        return label
