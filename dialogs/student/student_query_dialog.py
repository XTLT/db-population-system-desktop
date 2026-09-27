from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QComboBox, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.config import FONT_NAME, FONT_SIZE, GRADES, GRADE_DISPLAY, BTN_SAVE_COLOR
from core.database import search_students, get_all_students, batch_update_school, batch_set_left_behind, get_session, Person, StudentEducation
from network.client import get_server_url
class StudentQueryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("学生信息查询")
        self.setMinimumSize(1000, 600)
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("学校："))
        self.txt_school = QLineEdit()
        self.txt_school.setPlaceholderText("全部")
        filter_layout.addWidget(self.txt_school)

        filter_layout.addWidget(QLabel("年级："))
        self.cbo_grade = QComboBox()
        self.cbo_grade.addItem("")
        for g in GRADES:
            self.cbo_grade.addItem(GRADE_DISPLAY.get(g, g), g)
        filter_layout.addWidget(self.cbo_grade)

        filter_layout.addWidget(QLabel("班级："))
        self.txt_class = QLineEdit()
        self.txt_class.setPlaceholderText("全部")
        filter_layout.addWidget(self.txt_class)

        filter_layout.addWidget(QLabel("留守儿童："))
        self.cbo_left_behind = QComboBox()
        self.cbo_left_behind.addItems(["", "是", "否"])
        filter_layout.addWidget(self.cbo_left_behind)

        btn_search = QPushButton("查询")
        btn_search.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 8px;")
        btn_search.clicked.connect(self._search)
        filter_layout.addWidget(btn_search)
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        batch_layout = QHBoxLayout()
        batch_layout.addWidget(QLabel("批量设置学校："))
        self.txt_batch_school = QLineEdit()
        batch_layout.addWidget(self.txt_batch_school)
        btn_batch_school = QPushButton("应用")
        btn_batch_school.clicked.connect(self._batch_school)
        batch_layout.addWidget(btn_batch_school)

        batch_layout.addWidget(QLabel("留守儿童："))
        self.cbo_batch_left = QComboBox()
        self.cbo_batch_left.addItems(["是", "否"])
        batch_layout.addWidget(self.cbo_batch_left)
        btn_batch_left = QPushButton("批量设置")
        btn_batch_left.clicked.connect(self._batch_left_behind)
        batch_layout.addWidget(btn_batch_left)
        layout.addLayout(batch_layout)

    def _load_data(self, students=None):
        if students is None:
            if get_server_url():
                try:
                    from network.client import api_students
                    students = api_students()
                except Exception:
                    students = []
            else:
                students = get_all_students()

        headers = ["姓名", "身份证号", "学校", "年级", "班级", "监护人", "留守儿童", "状态"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(students))

        for row_idx, s in enumerate(students):
            if isinstance(s, dict):
                person_id = s.get('person_id', '')
                name = s.get('name', '')
                id_card = s.get('id_card', '')
                school_name = s.get('school_name', '')
                grade = s.get('grade', '')
                class_name = s.get('class_name', '')
                guardian = s.get('guardian', '')
                is_left_behind = s.get('is_left_behind', '')
                student_status = s.get('student_status', '')
                grade_display = GRADE_DISPLAY.get(grade, grade)
            else:
                person_id = s.person_id
                person = self._get_person(s.person_id)
                name = person.name if person else ""
                id_card = s.id_card
                school_name = s.school_name
                grade = s.grade
                class_name = s.class_name
                guardian = s.guardian
                is_left_behind = s.is_left_behind
                student_status = s.student_status
                grade_display = GRADE_DISPLAY.get(s.grade, s.grade)
            values = [name, id_card, school_name, grade_display, class_name, guardian, is_left_behind, student_status]
            for col_idx, val in enumerate(values):
                item = QTableWidgetItem(str(val) if val else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col_idx == 0:
                    item.setData(Qt.ItemDataRole.UserRole, person_id)
                self.table.setItem(row_idx, col_idx, item)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _get_person(self, person_id):
        if get_server_url():
            try:
                from network.client import api_person
                data = api_person(person_id)
                return type('Person', (), data)()
            except Exception:
                return None
        else:
            session = get_session()
            try:
                return session.query(Person).filter(Person.id == person_id).first()
            finally:
                session.close()

    def _search(self):
        school = self.txt_school.text().strip() or None
        grade = self.cbo_grade.currentData() or None
        class_name = self.txt_class.text().strip() or None
        left_behind = self.cbo_left_behind.currentText() or None

        if get_server_url():
            try:
                from network.client import api_students_search
                students = api_students_search(school, grade, class_name, left_behind)
            except Exception:
                students = []
        else:
            students = search_students(school, grade, class_name, left_behind)
        self._load_data(students)

    def _get_selected_person_ids(self):
        selected = []
        seen_rows = set()
        for item in self.table.selectedItems():
            row = item.row()
            if row in seen_rows:
                continue
            seen_rows.add(row)
            name_item = self.table.item(row, 0)
            if name_item:
                pid = name_item.data(Qt.ItemDataRole.UserRole)
                if pid:
                    selected.append(pid)
        return list(set(selected))

    def _batch_school(self):
        person_ids = self._get_selected_person_ids()
        if not person_ids:
            QMessageBox.warning(self, "提示", "请先选择学生！")
            return
        school = self.txt_batch_school.text().strip()
        if not school:
            QMessageBox.warning(self, "提示", "请输入学校名称！")
            return
        if get_server_url():
            try:
                from network.client import api_update_education
                for pid in person_ids:
                    api_update_education(pid, {'school_name': school})
                QMessageBox.information(self, "成功", f"已更新 {len(person_ids)} 名学生的学校！")
                self._search()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"批量更新失败：{str(e)}")
        else:
            batch_update_school(person_ids, school)
            QMessageBox.information(self, "成功", f"已更新 {len(person_ids)} 名学生的学校！")
            self._search()

    def _batch_left_behind(self):
        person_ids = self._get_selected_person_ids()
        if not person_ids:
            QMessageBox.warning(self, "提示", "请先选择学生！")
            return
        value = self.cbo_batch_left.currentText()
        if get_server_url():
            try:
                from network.client import api_update_education
                for pid in person_ids:
                    api_update_education(pid, {'is_left_behind': value})
                QMessageBox.information(self, "成功", f"已设置 {len(person_ids)} 名学生的留守儿童状态！")
                self._search()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"批量设置失败：{str(e)}")
        else:
            batch_set_left_behind(person_ids, value)
            QMessageBox.information(self, "成功", f"已设置 {len(person_ids)} 名学生的留守儿童状态！")
            self._search()
