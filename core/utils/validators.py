# -*- coding: utf-8 -*-
"""身份证号 / 电话号码格式校验。

口径以服务端 utils/common/validate_id_card.py、validate_phone.py 为基准，
desktop / mobile / server 三端的判定与提示文案保持一致。

统一规则：
    身份证：去掉所有空白后必须 18 位（前 17 位数字 + 末位数字或 X），
            校验位合法，出生日期合法；15 位不再支持录入。
    电话：  去掉首尾空白并剔除 "-" 与空白后，仅接受 11 位手机号，
            空值放行，座机拒绝。
"""

import re
from datetime import date


def clean_digits(text, allow_x=False):
    """把输入清洗成纯号码：去掉空格、横杠等一切非号码字符（允许的话保留 X/x 并转大写）。
    用于身份证、电话号码这类编码字段，粘贴带空格的号码也能自动纠正。"""
    allowed = '0123456789Xx' if allow_x else '0123456789'
    cleaned = ''.join(ch for ch in (text or '') if ch in allowed)
    return cleaned.replace('x', 'X') if allow_x else cleaned


def install_digit_filter(line_edit, allow_x=False):
    """给 QLineEdit 挂即时清洗：非法字符（含空格）一输入/一粘贴就被删掉，
    用户看到的始终是干净号码，不会等到点保存才报错。"""
    def _clean(text):
        cleaned = clean_digits(text, allow_x)
        if cleaned != text:
            pos = line_edit.cursorPosition()
            line_edit.setText(cleaned)
            line_edit.setCursorPosition(min(pos, len(cleaned)))

    line_edit.textChanged.connect(_clean)


def validate_id_card(id_card):
    """校验身份证号：去掉所有空白后必须 18 位（前 17 位数字 + 末位数字或 X），
    校验位合法，出生日期（年份 1900~今年、月份 1-12、日按大小月与闰年）合法。
    返回 (ok, msg)，提示文案与服务端基准一致。"""
    id_card = re.sub(r'\s+', '', id_card or '').upper()

    if not id_card:
        return False, "身份证号不能为空"
    if len(id_card) != 18:
        return False, "身份证号必须为18位"
    # 用 ASCII [0-9] 而不是 str.isdigit()：isdigit() 会把全角数字也算成数字，
    # 而 Dart 端的 \d 只认 ASCII，两边会分叉（2026-11-06 由共享向量发现）。
    if not re.fullmatch(r'[0-9]{17}', id_card[:17]):
        return False, "身份证号前17位必须为数字"
    if not (re.fullmatch(r'[0-9]', id_card[17]) or id_card[17] == 'X'):
        return False, "身份证号最后一位必须为数字或X"

    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    total = sum(int(id_card[i]) * weights[i] for i in range(17))
    if id_card[17] != check_codes[total % 11]:
        return False, "身份证号校验位错误"

    year = int(id_card[6:10])
    month = int(id_card[10:12])
    day = int(id_card[12:14])

    if year < 1900 or year > date.today().year:
        return False, "身份证号出生年份无效"
    if month < 1 or month > 12:
        return False, "身份证号出生月份无效"
    if day < 1 or day > 31:
        return False, "身份证号出生日期无效"
    if month in (4, 6, 9, 11) and day > 30:
        return False, "身份证号出生日期无效"
    if month == 2:
        is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        if day > (29 if is_leap else 28):
            return False, "身份证号出生日期无效"

    return True, ""


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
