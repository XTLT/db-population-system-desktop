"""电话号码校验（口径与服务端 utils/common/validate_phone.py 对齐）。"""

import re


def validate_phone(phone):
    """校验电话：去掉首尾空白并剔除 "-" 与空白后，可空；
    仅接受 11 位手机号 ^1[3-9]\\d{9}$（不校验座机，业务上只录手机号）。
    返回 (ok, msg)，提示文案与服务端基准一致。"""
    phone = re.sub(r'[-\s]', '', (phone or '').strip())

    if not phone:
        return True, ""

    if re.match(r'^1[3-9]\d{9}$', phone):
        return True, ""

    return False, "电话号码格式无效，请输入11位手机号"
