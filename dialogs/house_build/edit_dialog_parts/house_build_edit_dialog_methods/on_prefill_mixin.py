from .._imports import *
from .._consts import *
from ..funcs import *


class HouseBuildEditDialogOnPrefillMixin:
    def _on_prefill(self):
        id_card = self.txt_id_card.text().strip().upper()
        if not id_card:
            QMessageBox.information(self, "提示", "请先输入申请人身份证号。")
            return
        try:
            result = api_house_build_prefill(id_card)
        except Exception as e:
            QMessageBox.warning(self, "提示", f"从人口库带出失败：{e}")
            return
        if not result or not result.get('found'):
            QMessageBox.information(
                self, "提示",
                (result or {}).get('message') or '人口库中没有该身份证号，请手工填写。',
            )
            return

        self.e_owner_name.setText(result.get('owner_name', ''))
        combo_set(self.cmb_gender, result.get('owner_gender', ''))
        self.e_owner_age.setText(result.get('owner_age', ''))
        self.e_owner_phone.setText(result.get('owner_phone', ''))
        self.e_owner_hukou.setText(result.get('owner_hukou', ''))
        self.e_hu_hao.setText(result.get('hu_hao', ''))
        self.e_group_name.setText(result.get('group_name', ''))
        fill_member_rows(self.tbl_members, result.get('members') or [])
        self._show_history_note(result.get('hu_hao', ''), result.get('history') or [])
        QMessageBox.information(
            self, "完成",
            '已从人口库带出：%s，户内成员 %d 人。' % (
                result.get('owner_name', ''), len(result.get('members') or []))
        )

    def _show_history_note(self, hu_hao, history=None):
        if history:
            parts = []
            for item in history[:3]:
                parts.append('%s（%s，%s ㎡）' % (
                    item.get('app_no', ''),
                    (item.get('created_at') or '')[:10],
                    item.get('apply_land_area', '') or item.get('apply_area_num', ''),
                ))
            text = '该户已有 %d 条建房申请：%s' % (len(history), '；'.join(parts))
            if len(history) > 3:
                text += ' 等'
        elif hu_hao:
            text = '当前记录所属户号：%s（一户可多次申请，历史记录会保留）' % hu_hao
        else:
            text = ''
        self.lbl_history.setText(text)
