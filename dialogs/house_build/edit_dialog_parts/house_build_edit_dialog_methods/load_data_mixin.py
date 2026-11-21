from .._imports import *
from .._consts import *
from ..funcs import *


class HouseBuildEditDialogLoadDataMixin:
    def _load_data(self):
        data = api_house_build_get(self.app_id)
        if not data:
            raise ValueError("未取到申请数据")
        self.data = data

        self.txt_app_no.setText(data.get('app_no', ''))
        combo_set(self.cmb_status, data.get('status', 'draft'))
        self.txt_id_card.setText(data.get('owner_id_card', ''))

        self.e_owner_name.setText(data.get('owner_name', ''))
        combo_set(self.cmb_gender, data.get('owner_gender', ''))
        self.e_owner_age.setText(data.get('owner_age', ''))
        self.e_owner_phone.setText(data.get('owner_phone', ''))
        self.e_owner_hukou.setText(data.get('owner_hukou', ''))
        self.e_hu_hao.setText(data.get('hu_hao', ''))
        self.e_group_name.setText(data.get('group_name', ''))

        fill_member_rows(self.tbl_members, data.get('members') or [])

        self.e_apply_land_area.setText(data.get('apply_land_area', ''))
        self.e_building_area.setText(data.get('building_area', ''))
        self.e_cert_no.setText(data.get('cert_no', ''))
        combo_set(self.cmb_disposal, data.get('current_disposal', ''))
        self.e_disposal_other.setText(data.get('current_disposal_other', ''))
        self.e_current_land_area.setText(data.get('current_land_area', ''))
        self.e_foundation_area.setText(data.get('foundation_area', ''))
        self.e_east.setText(data.get('east_to', ''))
        self.e_south.setText(data.get('south_to', ''))
        self.e_west.setText(data.get('west_to', ''))
        self.e_north.setText(data.get('north_to', ''))
        combo_set(self.cmb_build_type, data.get('build_type', ''))
        combo_set(self.cmb_land_type, data.get('land_type', ''))
        self.e_house_floor_area.setText(data.get('house_floor_area', ''))
        self.e_floors.setText(data.get('floors', ''))
        self.e_building_height.setText(data.get('building_height', ''))
        combo_set(self.cmb_neighbor, data.get('neighbor_opinion', ''))
        combo_set(self.cmb_design, data.get('design_plan', ''))
        self.e_apply_reason.setPlainText(data.get('apply_reason', ''))
        self.e_village_opinion.setPlainText(data.get('village_opinion', ''))
        self.e_village_leader.setText(data.get('village_leader', ''))
        self.e_village_date.setText(data.get('village_date', ''))

        self.e_ap_land_area.setText(data.get('approval_land_area', ''))
        self.e_ap_foundation.setText(data.get('approval_foundation_area', ''))
        self.e_ap_address.setText(data.get('approval_address', ''))
        combo_set(self.cmb_ap_build_type, data.get('approval_build_type', ''))
        combo_set(self.cmb_ap_land_type, data.get('approval_land_type', ''))
        self.e_ap_floor_area.setText(data.get('approval_house_floor_area', ''))
        self.e_ap_floors.setText(data.get('approval_floors', ''))
        self.e_ap_height.setText(data.get('approval_height', ''))

        approvals = data.get('approvals') or {}
        for key, widgets in self.ap_widgets.items():
            item = approvals.get(key) or {}
            widgets['opinion'].setPlainText(item.get('opinion', ''))
            widgets['leader'].setText(item.get('leader', ''))
            widgets['date'].setText(item.get('date', ''))

        self._show_history_note(data.get('hu_hao', ''))
        # 审批表镜像字段以申请表为准
        self._sync_approval_from_apply()
