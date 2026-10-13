from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR
from core.database import add_person
from core.utils import calculate_age
from core.database import Person
from network.client import get_server_url
class AddDialog(QDialog):
    def __init__(self, hu_hao: str, parent=None):
        super().__init__(parent)
        self.hu_hao = hu_hao
        self.setWindowTitle("添加新成员")
        self.setFixedSize(520, 600)
        self._setup_ui()
        self._auto_fill_address()

    def _auto_fill_address(self):
        if get_server_url():
            try:
                from network.client import api_family
                members = api_family(self.hu_hao)
                for m in members:
                    addr = m.get('address', '') if isinstance(m, dict) else getattr(m, 'address', '')
                    if addr and addr.strip():
                        self.txt_address.setEnabled(True)
                        self.txt_address.setText(addr.strip())
                        self.txt_address.setEnabled(False)
                        grp = m.get('group_name', '') if isinstance(m, dict) else getattr(m, 'group_name', '')
                        if grp and grp.strip():
                            self.txt_group_name.setText(grp.strip())
                        return
            except Exception:
                pass
        else:
            from core.database import get_family_members
            members = get_family_members(self.hu_hao)
            for m in members:
                if m.address and m.address.strip():
                    self.txt_address.setEnabled(True)
                    self.txt_address.setText(m.address.strip())
                    self.txt_address.setEnabled(False)
                    grp = getattr(m, 'group_name', '') or ''
                    if grp and grp.strip():
                        self.txt_group_name.setText(grp.strip())
                    return

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(8)

        self.txt_name = QLineEdit()
        self.txt_id_card = QLineEdit()
        self.txt_relation = QLineEdit()
        self.txt_address = QLineEdit()
        self.txt_address.setEnabled(False)
        self.txt_group_name = QLineEdit()
        self.txt_age = QLineEdit()
        self.txt_age.setReadOnly(True)
        self.txt_phone = QLineEdit()
        self.cbo_is_dead = QComboBox()
        self.cbo_is_dead.addItems(["否", "是"])
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

        save_layout = QHBoxLayout()
        btn_save = QPushButton("保存")
        btn_save.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 10px;")
        btn_save.clicked.connect(self._save)
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 10px;")
        btn_cancel.clicked.connect(self.reject)
        save_layout.addWidget(btn_save)
        save_layout.addWidget(btn_cancel)
        layout.addLayout(save_layout)

        self.txt_id_card.textChanged.connect(self._on_id_card_changed)

    def _on_id_card_changed(self, text):
        age = calculate_age(text)
        if age:
            self.txt_age.setText(age)

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

        if get_server_url():
            data = {
                'hu_hao': self.hu_hao,
                'id_card': id_card,
                'name': name,
                'age': age,
                'address': self.txt_address.text().strip(),
                'group_name': self.txt_group_name.text().strip(),
                'relation': self.txt_relation.text().strip(),
                'is_dead': self.cbo_is_dead.currentText(),
                'phone': self.txt_phone.text().strip(),
                'social_card1': self.txt_social1.text().strip(),
                'poor_type': self.cbo_poor_type.currentText(),
                'remark': self.txt_remark.text().strip(),
                'disability': self.cbo_disability.currentText(),
                'disability_type': self.cbo_disability_type.currentText(),
                'dis_level': self.cbo_dis_level.currentText(),
                'dibao': self.cbo_dibao.currentText(),
                'jisheng': self.cbo_jisheng.currentText(),
                'tekun': self.cbo_tekun.currentText(),
                'tekun_type': self.cbo_tekun_type.currentText(),
            }
            try:
                from network.client import api_add_person
                result = api_add_person(data)
                if result.get('success'):
                    QMessageBox.information(self, "成功", "新成员添加成功！")
                    self.accept()
                else:
                    QMessageBox.critical(self, "错误", result.get('error', '添加失败'))
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加失败：{str(e)}")
        else:
            person = Person(
                id=f"new_{id_card}",
                hu_hao=self.hu_hao,
                id_card=id_card,
                name=name,
                age=age,
                address=self.txt_address.text().strip(),
                group_name=self.txt_group_name.text().strip(),
                relation=self.txt_relation.text().strip(),
                is_dead=self.cbo_is_dead.currentText(),
                phone=self.txt_phone.text().strip(),
                social_card1=self.txt_social1.text().strip(),
                poor_type=self.cbo_poor_type.currentText(),
                remark=self.txt_remark.text().strip(),
                disability=self.cbo_disability.currentText(),
                disability_type=self.cbo_disability_type.currentText(),
                dis_level=self.cbo_dis_level.currentText(),
                dibao=self.cbo_dibao.currentText(),
                jisheng=self.cbo_jisheng.currentText(),
                tekun=self.cbo_tekun.currentText(),
                tekun_type=self.cbo_tekun_type.currentText(),
            )

            try:
                add_person(person)
                QMessageBox.information(self, "成功", "新成员添加成功！")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加失败：{str(e)}")
