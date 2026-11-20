from .._imports import *
from .._consts import *
from ..funcs import *

CheckableComboBox = None

class ExportFilterDialogGetFiltersMixin:
    def get_filters(self) -> dict:
        return {
            "name": self.txt_name.text().strip(),
            "address": self.txt_address.text().strip(),
            "age_min": self.txt_age_min.text().strip(),
            "age_max": self.txt_age_max.text().strip(),
            "is_dead": self.cmb_is_dead.currentText(),
            "relation": self.cmb_relation.get_selected(),
            "disability": self.cmb_disability.get_selected(),
            "dis_level": self.cmb_dis_level.get_selected(),
            "poor_type": self.cmb_poor_type.get_selected(),
            "dibao": self.cmb_dibao.currentText(),
            "jisheng": self.cmb_jisheng.currentText(),
            "tekun": self.cmb_tekun.currentText(),
            "tekun_type": self.cmb_tekun_type.get_selected(),
            "land_area": self.cmb_land.currentText(),
            "local_welfare_forest_area": self.cmb_local_welfare_forest.currentText(),
            "national_welfare_forest_area": self.cmb_national_welfare_forest.currentText(),
            "commercial_forest_area": self.cmb_commercial_forest.currentText(),
        }
