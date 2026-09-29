from ._write_template import _write_template

TREATMENT_PAYMENT_COLUMNS = [
    "所属乡镇", "所属村", "费款所属期", "支付标志", "个人编号",
    "公民身份证号码", "姓名", "银行账号", "卡号", "金额", "失败原因",
]


def generate_treatment_payment_template(path):
    _write_template(path, "待遇发放", TREATMENT_PAYMENT_COLUMNS)
