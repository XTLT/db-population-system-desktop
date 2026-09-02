import os
import sys

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QPushButton, QLabel, QMessageBox, QScrollArea, QWidget,
    QTabWidget, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QPixmap, QFont

from core.config import (
    FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_ADD_COLOR, BTN_CANCEL_COLOR,
    PHOTO_TYPES, PHOTOS_DIR, GRADES, GRADE_DISPLAY, STUDENT_STATUSES
)
from core.database import (
    update_person, migrate_person,
    get_student_education, save_student_education, delete_student_education,
    get_education_history, get_family_members, Person, StudentEducation
)
from data.photo_manager import save_photo, delete_photo, get_photo_path, get_photo_status
from core.utils import calculate_age
from network.client import get_server_url


class EditDialog(QDialog):
    def __init__(self, person: Person, parent=None):
        super().__init__(parent)
        self.person = person
        self.setWindowTitle("编辑家庭成员信息")
        self.setMinimumSize(560, 700)
        self.resize(560, 700)
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_basic_tab(), "基本信息")
        self.tabs.addTab(self._create_education_tab(), "就读信息")
        layout.addWidget(self.tabs)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("添加家庭成员")
        btn_add.setStyleSheet(f"background-color: {BTN_ADD_COLOR}; color: white; font-weight: bold; padding: 8px;")
        btn_add.clicked.connect(self._add_member)
        btn_layout.addWidget(btn_add)
        layout.addLayout(btn_layout)

        save_layout = QHBoxLayout()
        btn_migrate = QPushButton("户籍迁出")
        btn_migrate.setStyleSheet("background-color: #FF6600; color: white; font-weight: bold; padding: 10px;")
        btn_migrate.clicked.connect(self._migrate_person)
        btn_delete = QPushButton("删除人员")
        btn_delete.setStyleSheet("background-color: #CC0000; color: white; font-weight: bold; padding: 10px;")
        btn_delete.clicked.connect(self._delete_person)
        btn_save = QPushButton("保存修改")
        btn_save.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 10px;")
        btn_save.clicked.connect(self._save)
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 10px;")
        btn_cancel.clicked.connect(self.reject)
        save_layout.addWidget(btn_migrate)
        save_layout.addWidget(btn_delete)
        save_layout.addWidget(btn_save)
        save_layout.addWidget(btn_cancel)
        layout.addLayout(save_layout)

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
        self.txt_relation = QLineEdit()
        self.txt_address = QLineEdit()
        self.txt_address.setEnabled(False)
        self.txt_age = QLineEdit()
        self.txt_age.setReadOnly(True)
        self.txt_phone = QLineEdit()
        self.txt_land_area = QLineEdit()
        self.txt_land_area.setPlaceholderText("亩")
        self.cbo_is_dead = QComboBox()
        self.cbo_is_dead.addItems(["否", "是"])
        self.txt_social1 = QLineEdit()
        self.txt_social2 = QLineEdit()
        self.txt_social3 = QLineEdit()
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
            ("年龄：", self.txt_age),
            ("电话号码：", self.txt_phone),
            ("土地面积：", self.txt_land_area),
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
        self.txt_guardian_phone.setPlaceholderText("监护人电话")

        self.cbo_is_left_behind = QComboBox()
        self.cbo_is_left_behind.addItems(["否", "是"])

        self.cbo_student_status = QComboBox()
        self.cbo_student_status.addItems(STUDENT_STATUSES)

        self.date_enrollment = QDateEdit()
        self.date_enrollment.setCalendarPopup(True)
        self.date_enrollment.setDate(QDate.currentDate())

        self.txt_graduation_date = QLineEdit()
        self.txt_graduation_date.setPlaceholderText("自动计算，如：2029-06")

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

        return tab

    def _on_guardian_changed(self, index):
        phone = self.cbo_guardian.currentData()
        if phone and phone != "无":
            self.txt_guardian_phone.setText(phone)

    def _on_grade_changed(self, index):
        grade_code = self.cbo_grade.currentData()
        if grade_code:
            from core.utils import calculate_enrollment_date
            enrollment_date = calculate_enrollment_date(grade_code)
            if enrollment_date:
                try:
                    self.date_enrollment.setDate(QDate.fromString(enrollment_date, "yyyy-MM-dd"))
                except Exception:
                    pass
            self._update_graduation_date(grade_code)

    def _update_graduation_date(self, grade_code):
        grade_years = {
            'G1': 6, 'G2': 5, 'G3': 4, 'G4': 3, 'G5': 2, 'G6': 1,
            'G7': 3, 'G8': 2, 'G9': 1,
            'G10': 3, 'G11': 2, 'G12': 1,
        }
        total_years = grade_years.get(grade_code, 0)
        if total_years > 0:
            from core.utils import calculate_enrollment_date
            enrollment_date = calculate_enrollment_date(grade_code)
            if enrollment_date:
                try:
                    enroll_year = int(enrollment_date[:4])
                    grad_year = enroll_year + total_years
                    self.txt_graduation_date.setText(f"{grad_year}-06")
                except Exception:
                    pass

    def _on_disability_changed(self, text):
        is_disabled = (text == "是")
        self.cbo_disability_type.setVisible(is_disabled)
        self.cbo_disability_type_label.setVisible(is_disabled)
        self.cbo_dis_level.setVisible(is_disabled)
        self.cbo_dis_level_label.setVisible(is_disabled)

    def _on_tekun_changed(self, text):
        is_tekun = (text == "是")
        self.cbo_tekun_type.setVisible(is_tekun)
        self.cbo_tekun_type_label.setVisible(is_tekun)

    def _load_data(self):
        p = self.person
        self.txt_name.setText(p.name)
        self.txt_id_card.setText(p.id_card)
        self.txt_relation.setText(p.relation)
        self.txt_address.setText(p.address)
        self.txt_age.setText(p.age)
        self.txt_phone.setText(p.phone if p.phone != "无" else "")
        self.txt_land_area.setText(getattr(p, 'land_area', '') or "")
        self.cbo_is_dead.setCurrentText("是" if p.is_dead == "是" else "否")
        self.txt_social1.setText(p.social_card1 if p.social_card1 != "无" else "")
        self.txt_social2.setText(p.social_card2 if p.social_card2 != "无" else "")
        self.txt_social3.setText(p.social_card3 if p.social_card3 != "无" else "")
        poor_val = p.poor_type if p.poor_type != "无" else ""
        idx = self.cbo_poor_type.findText(poor_val)
        if idx >= 0:
            self.cbo_poor_type.setCurrentIndex(idx)
        self.txt_remark.setText(p.remark if p.remark != "无" else "")
        dis_val = p.disability if p.disability != "无" else ""
        idx = self.cbo_disability.findText(dis_val)
        if idx >= 0:
            self.cbo_disability.setCurrentIndex(idx)
        dis_type_val = getattr(p, 'disability_type', '') or ''
        if dis_type_val == "无":
            dis_type_val = ""
        idx = self.cbo_disability_type.findText(dis_type_val)
        if idx >= 0:
            self.cbo_disability_type.setCurrentIndex(idx)
        dis_level_val = p.dis_level if p.dis_level != "无" else ""
        idx = self.cbo_dis_level.findText(dis_level_val)
        if idx >= 0:
            self.cbo_dis_level.setCurrentIndex(idx)
        self._on_disability_changed(dis_val)
        dibao_val = p.dibao if p.dibao != "无" else ""
        idx = self.cbo_dibao.findText(dibao_val)
        if idx >= 0:
            self.cbo_dibao.setCurrentIndex(idx)
        else:
            self.cbo_dibao.setCurrentIndex(0)
        jisheng_val = p.jisheng if p.jisheng != "无" else ""
        idx = self.cbo_jisheng.findText(jisheng_val)
        if idx >= 0:
            self.cbo_jisheng.setCurrentIndex(idx)
        tekun_val = getattr(p, 'tekun', '') or ''
        if tekun_val == "无":
            tekun_val = ""
        idx = self.cbo_tekun.findText(tekun_val)
        if idx >= 0:
            self.cbo_tekun.setCurrentIndex(idx)
        else:
            self.cbo_tekun.setCurrentIndex(0)
        tekun_type_val = getattr(p, 'tekun_type', '') or ''
        if tekun_type_val == "无":
            tekun_type_val = ""
        idx = self.cbo_tekun_type.findText(tekun_type_val)
        if idx >= 0:
            self.cbo_tekun_type.setCurrentIndex(idx)
        else:
            self.cbo_tekun_type.setCurrentIndex(0)
        self._on_tekun_changed(tekun_val)
        self._load_current_photo()
        self._load_education_data()

    def _load_education_data(self):
        if get_server_url():
            try:
                from network.client import api_person
                data = api_person(self.person.id)
                edu_data = data.get('education')
                if edu_data:
                    self.txt_school.setText(edu_data.get('school_name', ''))
                    grade = edu_data.get('grade', '')
                    grade_set = False
                    for i in range(self.cbo_grade.count()):
                        if self.cbo_grade.itemData(i) == grade:
                            self.cbo_grade.setCurrentIndex(i)
                            grade_set = True
                            break
                    if not grade_set and grade:
                        for i in range(self.cbo_grade.count()):
                            if self.cbo_grade.itemText(i) == grade:
                                self.cbo_grade.setCurrentIndex(i)
                                grade_set = True
                                break
                    if not grade_set and grade:
                        self.cbo_grade.setEditText(grade)
                    self.txt_class.setText(edu_data.get('class_name', ''))
                    self.cbo_guardian.setCurrentText(edu_data.get('guardian', ''))
                    self.txt_guardian_phone.setText(edu_data.get('guardian_phone', ''))
                    self.cbo_is_left_behind.setCurrentText(edu_data.get('is_left_behind', '否'))
                    self.cbo_student_status.setCurrentText(edu_data.get('student_status', ''))
                    enrollment_date = edu_data.get('enrollment_date', '')
                    if enrollment_date:
                        try:
                            self.date_enrollment.setDate(QDate.fromString(enrollment_date, "yyyy-MM-dd"))
                        except Exception:
                            pass
                    self.txt_graduation_date.setText(edu_data.get('graduation_date', ''))
            except Exception:
                pass
            self.history_table.setColumnCount(0)
            self.history_table.setRowCount(0)
        else:
            edu = get_student_education(self.person.id)
            if edu:
                self.txt_school.setText(edu.school_name)
                for i in range(self.cbo_grade.count()):
                    if self.cbo_grade.itemData(i) == edu.grade:
                        self.cbo_grade.setCurrentIndex(i)
                        break
                self.txt_class.setText(edu.class_name)
                self.cbo_guardian.setCurrentText(edu.guardian)
                self.txt_guardian_phone.setText(edu.guardian_phone)
                self.cbo_is_left_behind.setCurrentText(edu.is_left_behind)
                self.cbo_student_status.setCurrentText(edu.student_status)
                if edu.enrollment_date:
                    try:
                        self.date_enrollment.setDate(QDate.fromString(edu.enrollment_date, "yyyy-MM-dd"))
                    except Exception:
                        pass
                self.txt_graduation_date.setText(getattr(edu, 'graduation_date', '') or '')

            history = get_education_history(self.person.id)
            headers = ["日期", "学校", "年级", "班级", "状态", "原因"]
            self.history_table.setColumnCount(len(headers))
            self.history_table.setHorizontalHeaderLabels(headers)
            self.history_table.setRowCount(len(history))
            for row_idx, h in enumerate(history):
                values = [h.change_date, h.school_name, h.grade, h.class_name, h.student_status, h.change_reason]
                for col_idx, val in enumerate(values):
                    item = QTableWidgetItem(str(val) if val else "")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.history_table.setItem(row_idx, col_idx, item)
            self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _on_photo_type_changed(self, text):
        self._load_current_photo()

    def _load_current_photo(self):
        path = get_photo_path(
            self.cbo_photo_type.currentText(),
            self.txt_id_card.text(),
            self.txt_social1.text(),
            self.txt_social2.text(),
            self.txt_social3.text()
        )
        if not path and get_server_url():
            try:
                from network.client import api_download_photo
                import tempfile
                tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                tmp.close()
                if api_download_photo(self.person.id, tmp.name):
                    save_photo(
                        tmp.name,
                        self.cbo_photo_type.currentText(),
                        self.txt_id_card.text(),
                        self.txt_social1.text(),
                        self.txt_social2.text(),
                        self.txt_social3.text()
                    )
                    path = get_photo_path(
                        self.cbo_photo_type.currentText(),
                        self.txt_id_card.text(),
                        self.txt_social1.text(),
                        self.txt_social2.text(),
                        self.txt_social3.text()
                    )
                os.unlink(tmp.name)
            except Exception:
                pass
        self.lbl_photo.clear()
        if path:
            pixmap = QPixmap(path)
            self.lbl_photo.setPixmap(pixmap.scaled(200, 150, Qt.AspectRatioMode.KeepAspectRatio))
            status = get_photo_status(
                self.txt_id_card.text(),
                self.txt_social1.text(),
                self.txt_social2.text(),
                self.txt_social3.text()
            )
            self.lbl_photo_status.setText(status)
        else:
            self.lbl_photo_status.setText("暂无照片")

    def _replace_photo(self):
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "选择要上传的照片", "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp)"
        )
        if path:
            save_photo(
                path,
                self.cbo_photo_type.currentText(),
                self.txt_id_card.text(),
                self.txt_social1.text(),
                self.txt_social2.text(),
                self.txt_social3.text()
            )
            if get_server_url():
                try:
                    from network.client import api_upload_photo
                    api_upload_photo(self.person.id, path, self.cbo_photo_type.currentText())
                except Exception as e:
                    QMessageBox.warning(self, "同步警告", f"照片已保存到本地，但同步到服务器失败：\n{str(e)}")
            self._load_current_photo()

    def _delete_photo(self):
        reply = QMessageBox.question(
            self, "确认删除", "确定要删除当前照片吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_photo(
                self.cbo_photo_type.currentText(),
                self.txt_id_card.text(),
                self.txt_social1.text(),
                self.txt_social2.text(),
                self.txt_social3.text()
            )
            if get_server_url():
                try:
                    from network.client import api_delete_photo_on_server
                    api_delete_photo_on_server(self.person.id, self.cbo_photo_type.currentText())
                except Exception as e:
                    QMessageBox.warning(self, "同步警告", f"照片已从本地删除，但同步删除服务器照片失败：\n{str(e)}")
            self._load_current_photo()

    def _save_photo_to(self):
        from PyQt6.QtWidgets import QFileDialog
        path = get_photo_path(
            self.cbo_photo_type.currentText(),
            self.txt_id_card.text(),
            self.txt_social1.text(),
            self.txt_social2.text(),
            self.txt_social3.text()
        )
        if not path:
            QMessageBox.information(self, "提示", "没有可保存的照片！")
            return
        dest, _ = QFileDialog.getSaveFileName(
            self, "保存照片", "", "图片文件 (*.jpg *.jpeg *.png *.bmp)"
        )
        if dest:
            from data.photo_manager import export_photo
            if export_photo(path, dest):
                QMessageBox.information(self, "成功", f"照片已保存到：{dest}")

    def _open_folder(self):
        from data.photo_manager import open_photos_folder
        open_photos_folder()

    def _add_member(self):
        from dialogs.person.add_dialog import AddDialog
        hu_hao = self.person.hu_hao
        dialog = AddDialog(hu_hao, self)
        if dialog.exec():
            self.accept()

    def _migrate_person(self):
        from dialogs.person.migration_dialog import MigrationDialog
        dialog = MigrationDialog(self.person.name, self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                if get_server_url():
                    from network.client import api_migrate_person
                    api_migrate_person(self.person.id, data)
                else:
                    migrate_person(
                        self.person.id,
                        data["date"],
                        data["place"],
                        data["reason"]
                    )
                QMessageBox.information(self, "成功", f"已将 {self.person.name} 标记为户籍迁出！")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"操作失败：{str(e)}")

    def _delete_person(self):
        reply1 = QMessageBox.question(
            self, "确认删除",
            f"确定要删除人员 {self.person.name} 吗？\n删除后可在「找回」功能中恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply1 == QMessageBox.StandardButton.Yes:
            reply2 = QMessageBox.question(
                self, "再次确认",
                f"请再次确认：是否删除 {self.person.name}？\n此操作会将该人员移入回收站。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply2 == QMessageBox.StandardButton.Yes:
                try:
                    if get_server_url():
                        from network.client import api_delete_person
                        api_delete_person(self.person.id)
                    else:
                        from core.database import delete_person as do_delete
                        do_delete(self.person.id)
                    QMessageBox.information(self, "成功", f"已将 {self.person.name} 移入回收站！")
                    self.accept()
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"删除失败：{str(e)}")

    def _save(self):
        name = self.txt_name.text().strip()
        id_card = self.txt_id_card.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "姓名不能为空！")
            return
        if not id_card:
            QMessageBox.warning(self, "提示", "身份证号不能为空！")
            return
        age = self.txt_age.text().strip()
        if age and not age.isdigit():
            QMessageBox.warning(self, "提示", "年龄必须是数字！")
            return

        new_land_area = self.txt_land_area.text().strip()
        old_land_area = getattr(self.person, 'land_area', '') or ''
        land_changed = new_land_area != old_land_area
        land_reason = ""

        if land_changed:
            from PyQt6.QtWidgets import QInputDialog
            land_reason, ok = QInputDialog.getText(
                self, "土地面积变更",
                f"土地面积从「{old_land_area or '空'}」变更为「{new_land_area or '空'}」\n\n请输入变更原因：",
            )
            if not ok or not land_reason.strip():
                QMessageBox.warning(self, "提示", "土地面积变更时必须填写变更原因！")
                return
            land_reason = land_reason.strip()

        if get_server_url():
            from network.client import api_update_person
            data = {
                'name': name,
                'id_card': id_card,
                'age': age,
                'relation': self.txt_relation.text().strip(),
                'address': self.txt_address.text().strip(),
                'phone': self.txt_phone.text().strip() or "无",
                'is_dead': self.cbo_is_dead.currentText(),
                'land_area': new_land_area,
                'social_card1': self.txt_social1.text().strip() or "无",
                'social_card2': self.txt_social2.text().strip() or "无",
                'social_card3': self.txt_social3.text().strip() or "无",
                'poor_type': self.cbo_poor_type.currentText() or "无",
                'remark': self.txt_remark.text().strip() or "无",
                'disability': self.cbo_disability.currentText() or "无",
                'disability_type': self.cbo_disability_type.currentText() or "无",
                'dis_level': self.cbo_dis_level.currentText() or "无",
                'dibao': self.cbo_dibao.currentText() or "无",
                'jisheng': self.cbo_jisheng.currentText() or "无",
                'tekun': self.cbo_tekun.currentText() or "无",
                'tekun_type': self.cbo_tekun_type.currentText() or "无",
                'updated_at': getattr(self.person, 'updated_at', ''),
                'land_area_change_reason': land_reason
            }
            try:
                result = api_update_person(self.person.id, data)
                if result.get('success'):
                    self._save_education()
                    QMessageBox.information(self, "成功", "信息修改成功！")
                    self.accept()
                else:
                    QMessageBox.critical(self, "错误", result.get('error', '修改失败'))
            except Exception as e:
                QMessageBox.critical(self, "错误", f"修改失败：{str(e)}")
        else:
            self.person.name = name
            self.person.id_card = id_card
            self.person.age = age
            self.person.relation = self.txt_relation.text().strip()
            self.person.address = self.txt_address.text().strip()
            self.person.phone = self.txt_phone.text().strip() or "无"
            self.person.is_dead = self.cbo_is_dead.currentText()
            self.person.land_area = new_land_area
            if land_changed:
                from datetime import datetime
                self.person.land_area_change_reason = land_reason
                self.person.land_area_change_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.person.social_card1 = self.txt_social1.text().strip() or "无"
            self.person.social_card2 = self.txt_social2.text().strip() or "无"
            self.person.social_card3 = self.txt_social3.text().strip() or "无"
            self.person.poor_type = self.cbo_poor_type.currentText() or "无"
            self.person.remark = self.txt_remark.text().strip() or "无"
            self.person.disability = self.cbo_disability.currentText() or "无"
            self.person.disability_type = self.cbo_disability_type.currentText() or "无"
            self.person.dis_level = self.cbo_dis_level.currentText() or "无"
            self.person.dibao = self.cbo_dibao.currentText() or "无"
            self.person.jisheng = self.cbo_jisheng.currentText() or "无"
            self.person.tekun = self.cbo_tekun.currentText() or "无"
            self.person.tekun_type = self.cbo_tekun_type.currentText() or "无"

            try:
                update_person(self.person)
                self._save_education()
                QMessageBox.information(self, "成功", "信息修改成功！")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"修改失败：{str(e)}")

    def _save_education(self):
        school = self.txt_school.text().strip()
        grade_code = self.cbo_grade.currentData()
        grade_display = self.cbo_grade.currentText().strip() if not grade_code else ''
        class_name = self.txt_class.text().strip()
        graduation_date = self.txt_graduation_date.text().strip()

        if get_server_url():
            from network.client import api_update_education
            edu_data = {
                'school_name': school,
                'grade': grade_code or grade_display or '',
                'class_name': class_name,
                'guardian': self.cbo_guardian.currentText().strip(),
                'guardian_phone': self.txt_guardian_phone.text().strip(),
                'is_left_behind': self.cbo_is_left_behind.currentText(),
                'student_status': self.cbo_student_status.currentText(),
                'enrollment_date': self.date_enrollment.date().toString("yyyy-MM-dd"),
                'graduation_date': graduation_date,
            }
            try:
                api_update_education(self.person.id, edu_data)
            except Exception as e:
                QMessageBox.warning(self, "同步警告", f"就读信息保存到服务器失败：\n{str(e)}")
        elif school or grade_code or class_name:
            edu = StudentEducation(
                id=f"edu_{self.person.id}",
                person_id=self.person.id,
                id_card=self.person.id_card,
                school_name=school,
                grade=grade_code or "",
                class_name=class_name,
                guardian=self.cbo_guardian.currentText().strip(),
                guardian_phone=self.txt_guardian_phone.text().strip(),
                is_left_behind=self.cbo_is_left_behind.currentText(),
                student_status=self.cbo_student_status.currentText(),
                enrollment_date=self.date_enrollment.date().toString("yyyy-MM-dd"),
                graduation_date=graduation_date,
            )
            save_student_education(edu)
        else:
            delete_student_education(self.person.id)
