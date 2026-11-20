from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogSaveMixin:
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
        guardian_phone = self.txt_guardian_phone.text().strip()
        ok, msg = validate_phone(guardian_phone)
        if not ok:
            QMessageBox.warning(self, "提示", "监护人电话不对！")
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

        new_local_welfare_forest = self.txt_local_welfare_forest.text().strip()
        old_local_welfare_forest = getattr(self.person, 'local_welfare_forest_area', '') or ''
        local_welfare_forest_changed = new_local_welfare_forest != old_local_welfare_forest
        local_welfare_forest_reason = ""

        if local_welfare_forest_changed and old_local_welfare_forest:
            from PyQt6.QtWidgets import QInputDialog
            local_welfare_forest_reason, ok = QInputDialog.getText(
                self, "地方公益林变更",
                f"地方公益林从「{old_local_welfare_forest}」变更为「{new_local_welfare_forest or '空'}」\n\n请输入变更原因：",
            )
            if not ok or not local_welfare_forest_reason.strip():
                QMessageBox.warning(self, "提示", "地方公益林变更时必须填写变更原因！")
                return
            local_welfare_forest_reason = local_welfare_forest_reason.strip()

        new_national_welfare_forest = self.txt_national_welfare_forest.text().strip()
        old_national_welfare_forest = getattr(self.person, 'national_welfare_forest_area', '') or ''
        national_welfare_forest_changed = new_national_welfare_forest != old_national_welfare_forest
        national_welfare_forest_reason = ""

        if national_welfare_forest_changed and old_national_welfare_forest:
            from PyQt6.QtWidgets import QInputDialog
            national_welfare_forest_reason, ok = QInputDialog.getText(
                self, "国家公益林变更",
                f"国家公益林从「{old_national_welfare_forest}」变更为「{new_national_welfare_forest or '空'}」\n\n请输入变更原因：",
            )
            if not ok or not national_welfare_forest_reason.strip():
                QMessageBox.warning(self, "提示", "国家公益林变更时必须填写变更原因！")
                return
            national_welfare_forest_reason = national_welfare_forest_reason.strip()

        new_commercial_forest = self.txt_commercial_forest.text().strip()
        old_commercial_forest = getattr(self.person, 'commercial_forest_area', '') or ''
        commercial_forest_changed = new_commercial_forest != old_commercial_forest
        commercial_forest_reason = ""

        if commercial_forest_changed and old_commercial_forest:
            from PyQt6.QtWidgets import QInputDialog
            commercial_forest_reason, ok = QInputDialog.getText(
                self, "非国有天然商品林变更",
                f"非国有天然商品林从「{old_commercial_forest}」变更为「{new_commercial_forest or '空'}」\n\n请输入变更原因：",
            )
            if not ok or not commercial_forest_reason.strip():
                QMessageBox.warning(self, "提示", "非国有天然商品林变更时必须填写变更原因！")
                return
            commercial_forest_reason = commercial_forest_reason.strip()

        new_is_dead = self.cbo_is_dead.currentText()
        old_is_dead = getattr(self.person, 'is_dead', '') or '否'
        death_date_value = self._death_date_value()
        if new_is_dead == '是' and old_is_dead != '是' and not death_date_value:
            QMessageBox.warning(self, "提示", "改为死亡时必须填写死亡时间！")
            return

        if get_server_url():
            from network.client import api_update_person
            data = {
                'name': name,
                'id_card': id_card,
                'age': age,
                'relation': self.txt_relation.currentText().strip(),
                'address': self.txt_address.text().strip(),
                'group_name': self.txt_group_name.text().strip(),
                'phone': self.txt_phone.text().strip(),
                'is_dead': new_is_dead,
                'death_date': death_date_value,
                'land_area': new_land_area,
                'local_welfare_forest_area': new_local_welfare_forest,
                'national_welfare_forest_area': new_national_welfare_forest,
                'commercial_forest_area': new_commercial_forest,
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
                'updated_at': getattr(self.person, 'updated_at', ''),
                'land_area_change_reason': land_reason,
                'local_welfare_forest_change_reason': local_welfare_forest_reason,
                'national_welfare_forest_change_reason': national_welfare_forest_reason,
                'commercial_forest_change_reason': commercial_forest_reason
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
            self.person.relation = self.txt_relation.currentText().strip()
            self.person.address = self.txt_address.text().strip()
            self.person.group_name = self.txt_group_name.text().strip()
            self.person.phone = self.txt_phone.text().strip()
            self.person.is_dead = new_is_dead
            self.person.death_date = death_date_value
            self.person.land_area = new_land_area
            if land_changed:
                from datetime import datetime
                self.person.land_area_change_reason = land_reason
                self.person.land_area_change_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.person.local_welfare_forest_area = new_local_welfare_forest
            if local_welfare_forest_changed and local_welfare_forest_reason:
                from datetime import datetime
                self.person.local_welfare_forest_change_reason = local_welfare_forest_reason
                self.person.local_welfare_forest_change_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.person.national_welfare_forest_area = new_national_welfare_forest
            if national_welfare_forest_changed and national_welfare_forest_reason:
                from datetime import datetime
                self.person.national_welfare_forest_change_reason = national_welfare_forest_reason
                self.person.national_welfare_forest_change_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.person.commercial_forest_area = new_commercial_forest
            if commercial_forest_changed and commercial_forest_reason:
                from datetime import datetime
                self.person.commercial_forest_change_reason = commercial_forest_reason
                self.person.commercial_forest_change_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.person.social_card1 = self.txt_social1.text().strip()
            self.person.poor_type = self.cbo_poor_type.currentText()
            self.person.remark = self.txt_remark.text().strip()
            self.person.disability = self.cbo_disability.currentText()
            self.person.disability_type = self.cbo_disability_type.currentText()
            self.person.dis_level = self.cbo_dis_level.currentText()
            self.person.dibao = self.cbo_dibao.currentText()
            self.person.jisheng = self.cbo_jisheng.currentText()
            self.person.tekun = self.cbo_tekun.currentText()
            self.person.tekun_type = self.cbo_tekun_type.currentText()

            try:
                update_person(self.person)
                self._save_education()
                QMessageBox.information(self, "成功", "信息修改成功！")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"修改失败：{str(e)}")
