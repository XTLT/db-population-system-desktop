from .._imports import *
from .._consts import *
from ..funcs import *


class HouseBuildEditDialogCollectDataMixin:
    def _collect_data(self):
        owner_name = self.e_owner_name.text().strip()
        owner_id_card = self.txt_id_card.text().strip().upper()
        apply_land_area = self.e_apply_land_area.text().strip()
        if not owner_name:
            QMessageBox.warning(self, "提示", "申请人姓名不能为空。")
            self.tabs.setCurrentIndex(0)
            self.e_owner_name.setFocus()
            return None
        if not owner_id_card:
            QMessageBox.warning(self, "提示", "申请人身份证号不能为空（用于从人口库关联）。")
            self.txt_id_card.setFocus()
            return None
        if not apply_land_area:
            QMessageBox.warning(self, "提示", "申请宅基地面积不能为空，该项会写入数据库面积字段用于统计。")
            self.e_apply_land_area.setFocus()
            return None

        approvals = {}
        for key, widgets in self.ap_widgets.items():
            approvals[key] = {
                'opinion': widgets['opinion'].toPlainText().strip(),
                'leader': widgets['leader'].text().strip(),
                'date': widgets['date'].text().strip(),
            }

        return {
            'owner_name': owner_name,
            'owner_gender': text_of(self.cmb_gender),
            'owner_age': self.e_owner_age.text().strip(),
            'owner_phone': self.e_owner_phone.text().strip(),
            'owner_id_card': owner_id_card,
            'owner_hukou': self.e_owner_hukou.text().strip(),
            'hu_hao': self.e_hu_hao.text().strip(),
            'group_name': self.e_group_name.text().strip(),
            'apply_land_area': apply_land_area,
            'building_area': self.e_building_area.text().strip(),
            'cert_no': self.e_cert_no.text().strip(),
            'current_disposal': text_of(self.cmb_disposal),
            'current_disposal_other': self.e_disposal_other.text().strip(),
            'current_land_area': self.e_current_land_area.text().strip(),
            'foundation_area': self.e_foundation_area.text().strip(),
            'east_to': self.e_east.text().strip(),
            'south_to': self.e_south.text().strip(),
            'west_to': self.e_west.text().strip(),
            'north_to': self.e_north.text().strip(),
            'build_type': text_of(self.cmb_build_type),
            'land_type': text_of(self.cmb_land_type),
            'house_floor_area': self.e_house_floor_area.text().strip(),
            'floors': self.e_floors.text().strip(),
            'building_height': self.e_building_height.text().strip(),
            'neighbor_opinion': text_of(self.cmb_neighbor),
            'design_plan': text_of(self.cmb_design),
            'apply_reason': self.e_apply_reason.toPlainText().strip(),
            'village_opinion': self.e_village_opinion.toPlainText().strip(),
            'village_leader': self.e_village_leader.text().strip(),
            'village_date': self.e_village_date.text().strip(),
            'approval_land_area': self.e_ap_land_area.text().strip(),
            # 与申请表重复的项统一取申请表，界面只读镜像
            'approval_foundation_area': self.e_foundation_area.text().strip(),
            'approval_address': self.e_ap_address.text().strip() or self.e_owner_hukou.text().strip(),
            'approval_build_type': text_of(self.cmb_build_type),
            'approval_land_type': text_of(self.cmb_land_type),
            'approval_house_floor_area': self.e_house_floor_area.text().strip(),
            'approval_floors': self.e_floors.text().strip(),
            'approval_height': self.e_building_height.text().strip(),
            'approvals': approvals,
            'status': text_of(self.cmb_status) or 'draft',
            'members': member_rows(self.tbl_members),
        }
