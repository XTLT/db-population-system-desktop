from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogLoadDataMixin:
    def _load_data(self):
        p = self.person
        self.txt_name.setText(p.name)
        self.txt_id_card.setText(p.id_card)
        self.txt_relation.setCurrentText(p.relation)
        self.txt_address.setText(p.address)
        self.txt_group_name.setText(getattr(p, 'group_name', '') or "")
        self.txt_age.setText(p.age)
        self.txt_phone.setText(p.phone if p.phone != "无" else "")
        self.txt_land_area.setText(getattr(p, 'land_area', '') or "")
        self.txt_local_welfare_forest.setText(getattr(p, 'local_welfare_forest_area', '') or "")
        self.txt_national_welfare_forest.setText(getattr(p, 'national_welfare_forest_area', '') or "")
        self.txt_commercial_forest.setText(getattr(p, 'commercial_forest_area', '') or "")
        self.cbo_is_dead.setCurrentText("是" if p.is_dead == "是" else "否")
        _death = getattr(p, 'death_date', '') or ''
        _qdeath = QDate.fromString(_death, "yyyy-MM-dd")
        self.dte_death_date.setDate(_qdeath if _qdeath.isValid() else QDate(1900, 1, 1))
        self._on_is_dead_changed(self.cbo_is_dead.currentText())
        self.txt_social1.setText(p.social_card1 if p.social_card1 != "无" else "")
        _c2 = p.social_card2 if p.social_card2 and p.social_card2 != "无" else ""
        _s2 = getattr(p, 'social_card2_source', '') or ''
        self.txt_social2.setText(_c2 + (f"（{_s2}）" if _s2 else ""))
        _c3 = p.social_card3 if p.social_card3 and p.social_card3 != "无" else ""
        _s3 = getattr(p, 'social_card3_source', '') or ''
        self.txt_social3.setText(_c3 + (f"（{_s3}）" if _s3 else ""))
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
