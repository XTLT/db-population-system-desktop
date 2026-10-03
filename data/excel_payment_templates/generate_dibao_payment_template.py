from ._write_template import _write_template

DIBAO_PAYMENT_COLUMNS = [
    "序号", "村名称", "救助类型", "人员姓名", "人员身份证号", "性别",
    "和申请人关系", "共同生活家庭成员", "享受保障人口数", "家庭保障总金额",
    "家庭最低生活基本保障金", "家庭特殊困难补助金", "家庭调剂金额",
    "特殊困难情形（分类施保）", "特殊困难补助金", "初始享受时间", "始发年月",
]


def generate_dibao_payment_template(path):
    _write_template(path, "低保发放", DIBAO_PAYMENT_COLUMNS)
