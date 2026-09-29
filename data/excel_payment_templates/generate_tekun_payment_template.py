from ._write_template import _write_template

TEKUN_PAYMENT_COLUMNS = [
    "所属乡镇", "所属村", "费款所属期", "支付标志", "个人编号",
    "公民身份证号码", "姓名", "银行账号", "卡号", "金额", "和申请人关系", "失败原因",
]


def generate_tekun_payment_template(path):
    _write_template(path, "特困发放", TEKUN_PAYMENT_COLUMNS)
