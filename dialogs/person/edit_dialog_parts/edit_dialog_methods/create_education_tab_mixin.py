from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogCreateEducationTabMixin:
    def _create_education_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        if get_server_url():
            try:
                from network.client import api_family
                family_data = api_family(self.person.hu_hao)
                family_members = [type('Member', (), m)() for m in family_data]
            except Exception:
                family_members = []
        else:
            family_members = get_family_members(self.person.hu_hao)

        form = QFormLayout()
        form.setSpacing(8)

        self.txt_school = QLineEdit()
        self.txt_school.setPlaceholderText("请输入学校名称")

        self.cbo_grade = QComboBox()
        self.cbo_grade.addItem("")
        for g in GRADES:
            self.cbo_grade.addItem(GRADE_DISPLAY.get(g, g), g)
        self.cbo_grade.currentIndexChanged.connect(self._on_grade_changed)

        self.txt_class = QLineEdit()

        self.cbo_guardian = QComboBox()
        self.cbo_guardian.setEditable(True)
        self.cbo_guardian.addItem("")
        for m in family_members:
            if m.id != self.person.id:
                self.cbo_guardian.addItem(m.name, m.phone)
        self.cbo_guardian.currentIndexChanged.connect(self._on_guardian_changed)

        self.txt_guardian_phone = QLineEdit()
        install_digit_filter(self.txt_guardian_phone)
        self.txt_guardian_phone.setPlaceholderText("监护人电话")

        self.cbo_is_left_behind = QComboBox()
        self.cbo_is_left_behind.addItems(["否", "是"])

        self.cbo_student_status = QComboBox()
        self.cbo_student_status.addItems(STUDENT_STATUSES)

        self.date_enrollment = QDateEdit()
        self.date_enrollment.setCalendarPopup(True)
        self.date_enrollment.setDate(QDate.currentDate())

        self.txt_graduation_date = QLineEdit()
        self.txt_graduation_date.setPlaceholderText("自动计算，如：2029-06-30")

        edu_fields = [
            ("学校名称：", self.txt_school),
            ("年级：", self.cbo_grade),
            ("班级：", self.txt_class),
            ("监护人：", self.cbo_guardian),
            ("监护人电话：", self.txt_guardian_phone),
            ("是否留守儿童：", self.cbo_is_left_behind),
            ("学生状态：", self.cbo_student_status),
            ("入学日期：", self.date_enrollment),
            ("毕业时间：", self.txt_graduation_date),
        ]

        for label_text, widget in edu_fields:
            label = QLabel(label_text)
            label.setFont(QFont(FONT_NAME, FONT_SIZE))
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            form.addRow(label, widget)

        layout.addLayout(form)

        history_label = QLabel("就读历史记录：")
        history_label.setFont(QFont(FONT_NAME, FONT_SIZE, QFont.Weight.Bold))
        layout.addWidget(history_label)

        self.history_table = QTableWidget()
        self.history_table.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setMaximumHeight(150)
        layout.addWidget(self.history_table)

        btn_row = QHBoxLayout()
        self.btn_delete_history = QPushButton("删除选中记录")
        self.btn_delete_history.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.btn_delete_history.clicked.connect(self._delete_selected_history)
        btn_row.addStretch(1)
        btn_row.addWidget(self.btn_delete_history)
        layout.addLayout(btn_row)

        return tab
