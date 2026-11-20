"""地力补贴导入的列名别名表。

key=内部字段，value=可能出现的列名（去掉单位括号后做子串匹配）。
同时识别“模板列名”与“导出/旧表短名”。
"""

LAND_FIELD_ALIASES = {
    "certified_area": ["确权颁证面积", "确权颁发面积", "耕地面积", "土地面积"],
    "subsidy_area":   ["补贴面积"],
    "base_standard":  ["基础补贴标准", "补贴标准", "基础标准", "耕地标准"],
    "rape_area":      ["其中种植油菜面积", "油菜面积"],
    "rape_amount":    ["其中种植油菜金额", "油菜金额"],
    "total_amount":   ["补贴总金额", "总金额", "补贴金额", "合计金额", "发放金额"],
    "phone":          ["电话号码", "电话"],
    "bank_account":   ["银行账号", "银行卡号", "打款账号"],
    "bank_name":      ["金融机构", "开户行", "银行机构"],
    "land_time":      ["上账时间", "到账时间", "发放时间"],
    "rape_standard":  ["油菜标准"],
    "card":           ["卡号"],
}

# 兼容旧代码里的私有名
_LAND_FIELD_ALIASES = LAND_FIELD_ALIASES
