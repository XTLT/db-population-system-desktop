# -*- coding: utf-8 -*-
"""身份证号 / 电话号码格式校验（规则与 mobile lib/utils/validators.dart 一致）"""

import re


def validate_id_card(id_card):
    """校验身份证号：18 位（前 17 位数字 + 校验位）/ 15 位全数字。
    返回 (ok, msg)，不通过时 msg 为用户可读提示。"""
    id_card = (id_card or '').strip().upper()
    if not id_card:
        return False, "身份证号码不对！"
    if len(id_card) == 18:
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        if not id_card[:17].isdigit():
            return False, "身份证号码不对！"
        total = sum(int(id_card[i]) * weights[i] for i in range(17))
        if id_card[17] != check_codes[total % 11]:
            return False, "身份证号码不对！"
        return True, ""
    if len(id_card) == 15:
        if id_card.isdigit():
            return True, ""
        return False, "身份证号码不对！"
    return False, "身份证号码不对！"


def validate_phone(phone):
    """校验电话：可空；11 位手机号 ^1[3-9]\\d{9}$；固话区号 0 开头 ^0\\d{2,3}-?\\d{7,8}$（10-12 位）。
    返回 (ok, msg)，不通过时 msg 为用户可读提示。"""
    phone = (phone or '').strip()
    if not phone:
        return True, ""
    if len(phone) == 11 and re.match(r'^1[3-9]\d{9}$', phone):
        return True, ""
    if re.match(r'^0\d{2,3}-?\d{7,8}$', phone):
        return True, ""
    return False, "电话号码不对！"
