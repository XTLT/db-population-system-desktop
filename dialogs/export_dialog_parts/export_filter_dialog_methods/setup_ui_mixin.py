from .._imports import *
from .._consts import *
from ..funcs import *

CheckableComboBox = None

class ExportFilterDialogSetupUiMixin:
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        filter_group = QGroupBox("筛选条件")
        filter_group.setFont(QFont(FONT_NAME, FONT_SIZE))
        form = QFormLayout()
        form.setSpacing(6)

        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("模糊匹配，留空不限")
        form.addRow("姓名：", self.txt_name)

        self.txt_address = QLineEdit()
        self.txt_address.setPlaceholderText("模糊匹配，留空不限")
        form.addRow("地址：", self.txt_address)

        age_layout = QHBoxLayout()
        self.txt_age_min = QLineEdit()
        self.txt_age_min.setPlaceholderText("最小")
        self.txt_age_min.setMaximumWidth(80)
        self.txt_age_max = QLineEdit()
        self.txt_age_max.setPlaceholderText("最大")
        self.txt_age_max.setMaximumWidth(80)
        age_layout.addWidget(self.txt_age_min)
        age_layout.addWidget(QLabel("~"))
        age_layout.addWidget(self.txt_age_max)
        age_layout.addStretch()
        form.addRow("年龄段：", age_layout)

        self.cmb_is_dead = QComboBox()
        self.cmb_is_dead.addItems(["全部", "否", "是"])
        form.addRow("是否死亡：", self.cmb_is_dead)

        self.cmb_relation = CheckableComboBox([
            "户主", "配偶", "子女", "父母", "兄弟姐妹",
            "祖父母", "孙子女", "儿媳", "女婿", "公婆", "岳父母",
            "孙媳", "孙婿", "其他"
        ])
        form.addRow("与户主关系：", self.cmb_relation)

        self.cmb_disability = CheckableComboBox([
            "肢体残疾", "视力残疾", "听力残疾",
            "智力残疾", "精神残疾", "多重残疾"
        ])
        form.addRow("残疾类别：", self.cmb_disability)

        self.cmb_dis_level = CheckableComboBox(["一级", "二级", "三级", "四级"])
        form.addRow("残疾等级：", self.cmb_dis_level)

        self.cmb_poor_type = CheckableComboBox([
            "脱贫户", "脱贫不稳定户",
            "边缘易致贫户", "突发严重困难户"
        ])
        form.addRow("脱贫户类型：", self.cmb_poor_type)

        self.cmb_dibao = QComboBox()
        self.cmb_dibao.addItems(["全部", "是", "否", "低保边缘家庭", "特困家庭"])
        form.addRow("低保：", self.cmb_dibao)

        self.cmb_jisheng = QComboBox()
        self.cmb_jisheng.addItems(["全部", "否", "是"])
        form.addRow("计生家庭：", self.cmb_jisheng)

        self.cmb_tekun = QComboBox()
        self.cmb_tekun.addItems(["全部", "是", "否"])
        form.addRow("特困供养：", self.cmb_tekun)

        self.cmb_tekun_type = CheckableComboBox(["集中供养", "散居特困"])
        form.addRow("供养类型：", self.cmb_tekun_type)

        self.cmb_land = QComboBox()
        self.cmb_land.addItems(["全部", "不为0", "空白"])
        form.addRow("土地面积：", self.cmb_land)

        self.cmb_local_welfare_forest = QComboBox()
        self.cmb_local_welfare_forest.addItems(["全部", "不为0", "空白"])
        form.addRow("地方公益林：", self.cmb_local_welfare_forest)

        self.cmb_national_welfare_forest = QComboBox()
        self.cmb_national_welfare_forest.addItems(["全部", "不为0", "空白"])
        form.addRow("国家公益林：", self.cmb_national_welfare_forest)

        self.cmb_commercial_forest = QComboBox()
        self.cmb_commercial_forest.addItems(["全部", "不为0", "空白"])
        form.addRow("非国有天然商品林：", self.cmb_commercial_forest)

        filter_group.setLayout(form)
        layout.addWidget(filter_group)

        self.lbl_count = QLabel("当前符合条件：计算中...")
        self.lbl_count.setFont(QFont(FONT_NAME, FONT_SIZE))
        layout.addWidget(self.lbl_count)

        btn_layout = QHBoxLayout()
        btn_reset = QPushButton("重置筛选")
        btn_reset.clicked.connect(self._reset_filters)
        btn_export = QPushButton("导出")
        btn_export.setStyleSheet("background-color: #0078D4; color: white; font-weight: bold; padding: 8px 24px;")
        btn_export.clicked.connect(self.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_reset)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_export)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
