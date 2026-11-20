from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogCreateBasicTabMixin:
    def _create_basic_tab(self):
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)

        form = QFormLayout()
        form.setSpacing(8)

        self.txt_name = QLineEdit()
        self.txt_id_card = QLineEdit()
        install_digit_filter(self.txt_id_card, allow_x=True)
        self.txt_relation = QComboBox()
        self.txt_relation.setEditable(True)
        self.txt_relation.addItems(RELATIONS)
        self.txt_relation.setCurrentText("")
        self.txt_address = QLineEdit()
        self.txt_address.setEnabled(False)
        self.txt_group_name = QLineEdit()
        self.txt_age = QLineEdit()
        self.txt_age.setReadOnly(True)
        self.txt_phone = QLineEdit()
        install_digit_filter(self.txt_phone)
        self.txt_land_area = QLineEdit()
        self.txt_land_area.setPlaceholderText("亩")
        self.txt_local_welfare_forest = QLineEdit()
        self.txt_local_welfare_forest.setPlaceholderText("亩")
        self.txt_national_welfare_forest = QLineEdit()
        self.txt_national_welfare_forest.setPlaceholderText("亩")
        self.txt_commercial_forest = QLineEdit()
        self.txt_commercial_forest.setPlaceholderText("亩")
        self.cbo_is_dead = QComboBox()
        self.cbo_is_dead.addItems(["否", "是"])
        self.cbo_is_dead.currentTextChanged.connect(self._on_is_dead_changed)
        # 死亡时间：选"是"后出现；由非死亡改为死亡时必填（存量已死亡人员不强制）
        self.dte_death_date = QDateEdit()
        self.dte_death_date.setCalendarPopup(True)
        self.dte_death_date.setDisplayFormat("yyyy-MM-dd")
        self.dte_death_date.setSpecialValueText("未填写")
        self.dte_death_date.setMinimumDate(QDate(1900, 1, 1))
        self.dte_death_date.setDate(QDate(1900, 1, 1))
        self.lbl_death_date = QLabel("死亡时间：")
        self.lbl_death_date.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.lbl_death_date.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_death_date.setVisible(False)
        self.dte_death_date.setVisible(False)
        self.txt_social1 = QLineEdit()
        self.txt_social2 = QLineEdit()
        self.txt_social2.setReadOnly(True)
        self.txt_social3 = QLineEdit()
        self.txt_social3.setReadOnly(True)
        self.cbo_poor_type = QComboBox()
        self.cbo_poor_type.addItems(["", "脱贫户", "脱贫不稳定户", "突发严重困难户", "边缘易致贫户"])
        self.txt_remark = QLineEdit()
        self.cbo_disability = QComboBox()
        self.cbo_disability.addItems(["", "是", "否"])
        self.cbo_disability.currentTextChanged.connect(self._on_disability_changed)
        self.cbo_disability_type = QComboBox()
        self.cbo_disability_type.addItems(["", "视力残疾", "听力残疾", "言语残疾", "肢体残疾", "智力残疾", "精神残疾", "多重残疾"])
        self.cbo_disability_type_label = QLabel("残疾类型：")
        self.cbo_disability_type_label.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.cbo_disability_type_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.cbo_disability_type.setVisible(False)
        self.cbo_disability_type_label.setVisible(False)
        self.cbo_dis_level = QComboBox()
        self.cbo_dis_level.addItems(["", "一级", "二级", "三级", "四级"])
        self.cbo_dis_level_label = QLabel("残疾等级：")
        self.cbo_dis_level_label.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.cbo_dis_level_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.cbo_dis_level.setVisible(False)
        self.cbo_dis_level_label.setVisible(False)
        self.cbo_dibao = QComboBox()
        self.cbo_dibao.addItems(["", "是", "否", "低保边缘家庭", "特困家庭"])
        self.cbo_jisheng = QComboBox()
        self.cbo_jisheng.addItems(["", "是", "否"])
        self.cbo_tekun = QComboBox()
        self.cbo_tekun.addItems(["", "是", "否"])
        self.cbo_tekun.currentTextChanged.connect(self._on_tekun_changed)
        self.cbo_tekun_type = QComboBox()
        self.cbo_tekun_type.addItems(["", "集中供养", "散居特困"])
        self.cbo_tekun_type_label = QLabel("供养类型：")
        self.cbo_tekun_type_label.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.cbo_tekun_type_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.cbo_tekun_type.setVisible(False)
        self.cbo_tekun_type_label.setVisible(False)

        fields = [
            ("姓名：", self.txt_name),
            ("身份证号：", self.txt_id_card),
            ("与户主关系：", self.txt_relation),
            ("地址：", self.txt_address),
            ("小组：", self.txt_group_name),
            ("年龄：", self.txt_age),
            ("电话号码：", self.txt_phone),
            ("土地面积：", self.txt_land_area),
            ("地方公益林：", self.txt_local_welfare_forest),
            ("国家公益林：", self.txt_national_welfare_forest),
            ("非国有天然商品林：", self.txt_commercial_forest),
            ("是否死亡：", self.cbo_is_dead),
            ("社保卡号1：", self.txt_social1),
            ("社保卡号2：", self.txt_social2),
            ("社保卡号3：", self.txt_social3),
            ("脱贫户或监测户：", self.cbo_poor_type),
            ("备注：", self.txt_remark),
            ("残疾：", self.cbo_disability),
        ]

        for label_text, widget in fields:
            label = QLabel(label_text)
            label.setFont(QFont(FONT_NAME, FONT_SIZE))
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            form.addRow(label, widget)

        form.addRow(self.lbl_death_date, self.dte_death_date)
        form.addRow(self.cbo_disability_type_label, self.cbo_disability_type)
        form.addRow(self.cbo_dis_level_label, self.cbo_dis_level)

        more_fields = [
            ("低保：", self.cbo_dibao),
            ("是否计生家庭：", self.cbo_jisheng),
            ("是否特困供养：", self.cbo_tekun),
        ]

        for label_text, widget in more_fields:
            label = QLabel(label_text)
            label.setFont(QFont(FONT_NAME, FONT_SIZE))
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            form.addRow(label, widget)

        form.addRow(self.cbo_tekun_type_label, self.cbo_tekun_type)

        layout.addLayout(form)

        photo_layout = QHBoxLayout()
        self.cbo_photo_type = QComboBox()
        self.cbo_photo_type.addItems(PHOTO_TYPES)
        self.cbo_photo_type.currentTextChanged.connect(self._on_photo_type_changed)
        photo_layout.addWidget(QLabel("照片类型："))
        photo_layout.addWidget(self.cbo_photo_type)
        self.lbl_photo_status = QLabel("暂无照片")
        self.lbl_photo_status.setFont(QFont(FONT_NAME, FONT_SIZE))
        photo_layout.addWidget(self.lbl_photo_status)
        layout.addLayout(photo_layout)

        self.lbl_photo = QLabel()
        self.lbl_photo.setFixedSize(200, 150)
        self.lbl_photo.setStyleSheet("border: 1px solid gray;")
        self.lbl_photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_photo, alignment=Qt.AlignmentFlag.AlignCenter)

        photo_btn_layout = QHBoxLayout()
        btn_replace = QPushButton("替换照片")
        btn_replace.clicked.connect(self._replace_photo)
        btn_delete_photo = QPushButton("删除照片")
        btn_delete_photo.clicked.connect(self._delete_photo)
        btn_save_photo = QPushButton("保存到...")
        btn_save_photo.clicked.connect(self._save_photo_to)
        btn_open = QPushButton("打开文件夹")
        btn_open.clicked.connect(self._open_folder)
        photo_btn_layout.addWidget(btn_replace)
        photo_btn_layout.addWidget(btn_delete_photo)
        photo_btn_layout.addWidget(btn_save_photo)
        photo_btn_layout.addWidget(btn_open)
        layout.addLayout(photo_btn_layout)

        scroll.setWidget(container)
        tab_layout = QVBoxLayout(tab)
        tab_layout.addWidget(scroll)
        return tab
