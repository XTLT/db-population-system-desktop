from .._imports import *
from .._consts import *
from ..funcs import *

CheckableComboBox = None

class ExportFilterDialogResetFiltersMixin:
    def _reset_filters(self):
        self.txt_name.clear()
        self.txt_address.clear()
        self.txt_age_min.clear()
        self.txt_age_max.clear()
        self.cmb_is_dead.setCurrentIndex(0)
        self.cmb_relation.reset_selection()
        self.cmb_disability.reset_selection()
        self.cmb_dis_level.reset_selection()
        self.cmb_poor_type.reset_selection()
        self.cmb_dibao.setCurrentIndex(0)
        self.cmb_jisheng.setCurrentIndex(0)
        self.cmb_tekun.setCurrentIndex(0)
        self.cmb_tekun_type.reset_selection()
        self.cmb_land.setCurrentIndex(0)
        self.cmb_local_welfare_forest.setCurrentIndex(0)
        self.cmb_national_welfare_forest.setCurrentIndex(0)
        self.cmb_commercial_forest.setCurrentIndex(0)
