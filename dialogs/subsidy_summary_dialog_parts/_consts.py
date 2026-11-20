"""原模块的模块级常量。"""
from ._imports import *

"""人员补贴汇总：一屏查看该人 6 个补贴模块的发放记录。"""

_LOCAL_MODULES = (
    ("dibao_payment", "低保", "period", "amount"),
    ("elderly_allowance", "高龄补贴", "period", "amount"),
    ("land_subsidy", "地力补贴", "subsidy_year", "total_amount"),
    ("disability_care_payment", "残疾护理补贴", "period", "amount"),
    ("pension_insurance", "养老保险", "period", "amount"),
    ("tekun_payment", "特困供养", "period", "amount"),
)

_HEADERS = ["补贴类型", "期间", "金额（元）", "银行账号", "发放状态", "村", "备注"]

__all__ = ['_LOCAL_MODULES', '_HEADERS']
