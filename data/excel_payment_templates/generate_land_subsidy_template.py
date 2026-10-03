from ._write_template import _write_template

LAND_SUBSIDY_COLUMNS = [
    "户主姓名", "身份证号", "电话号码", "银行账号", "金融机构",
    "发放金额", "耕地面积", "耕地标准", "油菜面积", "油菜标准", "油菜金额",
]


def generate_land_subsidy_template(path):
    _write_template(path, "地力补贴", LAND_SUBSIDY_COLUMNS)
