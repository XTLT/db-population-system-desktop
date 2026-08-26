from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt

from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR
from core.database import add_person, check_duplicate_id_card
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
        self.txt_age = QLineEdit()
        self.txt_age.setReadOnly(True)
        self.txt_phone = QLineEdit()
        self.cbo_is_dead = QComboBox()
        self.cbo_is_dead.addItems(["否", "是"])
        self.txt_social1 = QLineEdit()
        self.txt_social2 = QLineEdit()
        self.txt_social3 = QLineEdit()
        self.txt_poor_type = QLineEdit()
        self.txt_remark = QLineEdit()
        self.txt_disability = QLineEdit()
        self.txt_dis_level = QLineEdit()
        self.cbo_dibao = QComboBox()
        self.cbo_dibao.addItems(["", "是", "否", "低保边缘家庭", "特困家庭"])
        self.txt_jisheng = QLineEdit()
        self.cbo_tekun = QComboBox()
        self.cbo_tekun.addItems(["", "是", "否"])
        self.cbo_tekun_type = QComboBox()
        self.cbo_tekun_type.addItems(["", "集中供养", "散居特困"])

        fields = [
            ("姓名：", self.txt_name),
            ("身份证号：", self.txt_id_card),
            ("与户主关系：", self.txt_relation),
            ("地址：", self.txt_address),
            ("年龄：", self.txt_age),
            ("电话号码：", self.txt_phone),
            ("是否死亡：", self.cbo_is_dead),
            ("社保卡号1：", self.txt_social1),
            ("社保卡号2：", self.txt_social2),
            ("社保卡号3：", self.txt_social3),
            ("脱贫户或监测户：", self.txt_poor_type),
            ("备注：", self.txt_remark),
            ("残疾：", self.txt_disability),
            ("残疾等级：", self.txt_dis_level),
            ("低保：", self.cbo_dibao),
            ("是否计生家庭：", self.txt_jisheng),
            ("是否特困供养：", self.cbo_tekun),
            ("供养类型：", self.cbo_tekun_type),
        ]

        for label_text, widget in fields:
            label = QLabel(label_text)
            from PyQt6.QtGui import QFont
            label.setFont(QFont(FONT_NAME, FONT_SIZE))
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            form.addRow(label, widget)

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
            try:
                from network.client import api_check_duplicate
                if api_check_duplicate(self.hu_hao, id_card):
                    reply = QMessageBox.question(
                        self, "重复提醒", "该身份证号已存在于本户中，是否继续添加？",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.No:
                        return
            except Exception:
                pass

            data = {
                'hu_hao': self.hu_hao,
                'id_card': id_card,
                'name': name,
                'age': age,
                'address': self.txt_address.text().strip(),
                'relation': self.txt_relation.text().strip(),
                'is_dead': self.cbo_is_dead.currentText(),
                'phone': self.txt_phone.text().strip() or "无",
                'social_card1': self.txt_social1.text().strip() or "无",
                'social_card2': self.txt_social2.text().strip() or "无",
                'social_card3': self.txt_social3.text().strip() or "无",
                'poor_type': self.txt_poor_type.text().strip() or "无",
                'remark': self.txt_remark.text().strip() or "无",
                'disability': self.txt_disability.text().strip() or "无",
                'dis_level': self.txt_dis_level.text().strip() or "无",
                'dibao': self.cbo_dibao.currentText() or "无",
                'jisheng': self.txt_jisheng.text().strip() or "无",
                'tekun': self.cbo_tekun.currentText() or "无",
                'tekun_type': self.cbo_tekun_type.currentText() or "无",
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
            if check_duplicate_id_card(self.hu_hao, id_card):
                reply = QMessageBox.question(
                    self, "重复提醒", "该身份证号已存在于本户中，是否继续添加？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return

            person = Person(
                id=f"new_{id_card}",
                hu_hao=self.hu_hao,
                id_card=id_card,
                name=name,
                age=age,
                address=self.txt_address.text().strip(),
                relation=self.txt_relation.text().strip(),
                is_dead=self.cbo_is_dead.currentText(),
                phone=self.txt_phone.text().strip() or "无",
                social_card1=self.txt_social1.text().strip() or "无",
                social_card2=self.txt_social2.text().strip() or "无",
                social_card3=self.txt_social3.text().strip() or "无",
                poor_type=self.txt_poor_type.text().strip() or "无",
                remark=self.txt_remark.text().strip() or "无",
                disability=self.txt_disability.text().strip() or "无",
                dis_level=self.txt_dis_level.text().strip() or "无",
                dibao=self.cbo_dibao.currentText() or "无",
                jisheng=self.txt_jisheng.text().strip() or "无",
                tekun=self.cbo_tekun.currentText() or "无",
                tekun_type=self.cbo_tekun_type.currentText() or "无",
            )

            try:
                add_person(person)
                QMessageBox.information(self, "成功", "新成员添加成功！")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加失败：{str(e)}")
