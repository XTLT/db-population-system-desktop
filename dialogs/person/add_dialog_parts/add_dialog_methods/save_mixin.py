from .._imports import *
from .._consts import *
from ..funcs import *



class AddDialogSaveMixin:
    def _save(self):
        name = self.txt_name.text().strip()
        id_card = self.txt_id_card.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "姓名不能为空！")
            return
        if not id_card:
            QMessageBox.warning(self, "提示", "身份证号不能为空！")
            return
        ok, msg = validate_id_card(id_card)
        if not ok:
            QMessageBox.warning(self, "提示", msg)
            return
        phone = self.txt_phone.text().strip()
        ok, msg = validate_phone(phone)
        if not ok:
            QMessageBox.warning(self, "提示", msg)
            return
        age = self.txt_age.text().strip()
        if age and not age.isdigit():
            QMessageBox.warning(self, "提示", "年龄必须是数字！")
            return

        new_is_dead = self.cbo_is_dead.currentText()
        death_date_value = self._death_date_value()
        if new_is_dead == '是' and not death_date_value:
            QMessageBox.warning(self, "提示", "改为死亡时必须填写死亡时间！")
            return

        if get_server_url():
            data = {
                'hu_hao': self.hu_hao,
                'id_card': id_card,
                'name': name,
                'age': age,
                'address': self.txt_address.text().strip(),
                'group_name': self.txt_group_name.text().strip(),
                'relation': self.txt_relation.currentText().strip(),
                'is_dead': new_is_dead,
                'death_date': death_date_value,
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
                relation=self.txt_relation.currentText().strip(),
                is_dead=new_is_dead,
                death_date=death_date_value,
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
