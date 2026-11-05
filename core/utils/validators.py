# -*- coding: utf-8 -*-
"""身份证号 / 电话号码格式校验（规则与 mobile lib/utils/validators.dart 一致）"""

import re
from datetime import date


def validate_id_card(id_card):
    """校验身份证号：必须 18 位（前 17 位数字 + 校验位，最后一位可为 X），
    且出生年月日必须合法（与服务端 utils/common/validate_id_card.py 同一口径）。
    返回 (ok, msg)，不通过时 msg 为用户可读提示。"""
    id_card = (id_card or '').strip().upper()
    if not id_card:
        return False, "身份证号码不对！"
    if len(id_card) != 18:
        return False, "身份证号码不对！"
    if not id_card[:17].isdigit():
        return False, "身份证号码不对！"
    if not (id_card[17].isdigit() or id_card[17] == 'X'):
        return False, "身份证号码不对！"

    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    total = sum(int(id_card[i]) * weights[i] for i in range(17))
    if id_card[17] != check_codes[total % 11]:
        return False, "身份证号码不对！"

    # 出生年月日合法性（与服务端一致：年份 1900~今年、月份 1-12、
    # 日按大小月与闰年判断）
    try:
        year = int(id_card[6:10])
        month = int(id_card[10:12])
        day = int(id_card[12:14])
    except ValueError:
        return False, "身份证号码不对！"
    if year < 1900 or year > date.today().year:
        return False, "身份证号码不对！"
    if month < 1 or month > 12:
        return False, "身份证号码不对！"
    if day < 1 or day > 31:
        return False, "身份证号码不对！"
    if month in (4, 6, 9, 11) and day > 30:
        return False, "身份证号码不对！"
    if month == 2:
        is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        if day > (29 if is_leap else 28):
            return False, "身份证号码不对！"

    return True, ""


def validate_phone(phone):
    """校验电话：可空；仅 11 位手机号 ^1[3-9]\\d{9}$（不校验座机，业务上只录手机号）。
    返回 (ok, msg)，不通过时 msg 为用户可读提示。"""
    phone = (phone or '').strip()
    if not phone:
        return True, ""
    if len(phone) == 11 and re.match(r'^1[3-9]\d{9}$', phone):
        return True, ""
    return False, "电话号码不对！"
