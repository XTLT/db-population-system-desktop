from ._write_template import _write_template

PENSION_INSURANCE_COLUMNS = [
    "所属乡镇", "所属村", "费款所属期", "支付标志", "个人编号",
    "公民身份证号码", "享受定期待遇人员ID", "姓名", "银行账号", "金额", "失败原因",
]


def generate_pension_insurance_template(path):
    _write_template(path, "养老保险", PENSION_INSURANCE_COLUMNS)
