from .._imports import *
from .._consts import *
from ..funcs import *



class LandSubsidyViewDialogLoadYearsMixin:
    def _load_years(self):
        try:
            if self.is_network_mode:
                try:
                    from network.client import _request
                    data = _request('GET', '/api/land_subsidy/years')
                    years = data.get('years', [])
                except Exception as e:
                    print(f"网络获取年度失败: {e}")
                    years = []
            else:
                from data.excel_importer import get_all_land_subsidies
                all_data = get_all_land_subsidies()
                years = list(set(s.subsidy_year for s in all_data if s.subsidy_year))
                years.sort(reverse=True)

            self.cmb_year.clear()
            self.cmb_year.addItem("全部")
            for y in years:
                self.cmb_year.addItem(y)
        except Exception as e:
            print(f"加载年度失败: {e}")
