from ._write_template import _write_template

LAND_SUBSIDY_COLUMNS = [
    "姓名", "身份证号",
    "确权颁证面积", "补贴面积（亩）", "基础补贴标准（元/亩）",
    "其中种植油菜面积", "其中种植油菜金额", "补贴总金额（元）",
    "卡号",
]


def generate_land_subsidy_template(path):
    _write_template(path, "地力补贴", LAND_SUBSIDY_COLUMNS)
