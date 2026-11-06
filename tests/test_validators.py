# -*- coding: utf-8 -*-
"""desktop 端录入校验回归测试（标准库 unittest，零外部依赖）。

运行方式（在 desktop 仓库根目录）：
    venv_build\\Scripts\\python.exe -m unittest discover -s tests -v

口径基准：server 的 utils/common/validate_id_card.py、validate_phone.py。
本测试与 mobile 的 test/utils/validators_test.dart 使用同一批用例、同一套提示文案。

覆盖范围：
    - validate_id_card：去所有空白后 18 位 + 校验位 + 出生日期合法，15 位一律拒绝
    - validate_phone：剔掉 "-" 与空白后仅 11 位手机号，空值放行，座机拒绝
    - clean_digits：身份证/电话录入时的即时清洗（空格、横杠、字母）

注意：install_digit_filter 依赖 QLineEdit，需要 QApplication，不在本文件测试。
"""

import os
import sys
import unittest

# 允许直接 python -m unittest discover -s tests 从仓库根执行
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.utils.validators import (  # noqa: E402
    clean_digits,
    validate_id_card,
    validate_phone,
)

WEIGHTS = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
CHECK_CODES = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

PHONE_ERR = "电话号码格式无效，请输入11位手机号"


def make_id(prefix17):
    """补齐正确的校验位，得到校验位一定合法的 18 位号码。

    用途：测试出生日期分支时，号码必须先过校验位，否则会被校验位规则提前拦下，
    测不到日期逻辑。这是上一个发版里踩过的坑。
    """
    total = sum(int(prefix17[i]) * WEIGHTS[i] for i in range(17))
    return prefix17 + CHECK_CODES[total % 11]


class TestValidateIdCard(unittest.TestCase):
    def assert_ok(self, value):
        self.assertEqual(validate_id_card(value), (True, ""))

    def assert_bad(self, value, msg):
        ok, actual = validate_id_card(value)
        self.assertFalse(ok, f"{value!r} 应被判为非法")
        self.assertEqual(actual, msg, f"{value!r} 的提示文案与基准不一致")

    def test_valid_18_digit(self):
        self.assert_ok(make_id('52032519900101123'))
        self.assert_ok('11010519491231002X')  # 经典合法号，校验位为 X
        self.assert_ok(make_id('52032519920229123'))  # 1992 闰年 2 月 29 日

    def test_15_digit_rejected(self):
        # 方案二：15 位不再支持录入
        self.assert_bad('110105491231002', "身份证号必须为18位")
        self.assert_bad('520325900101123', "身份证号必须为18位")

    def test_wrong_check_digit(self):
        valid = make_id('52032519900101123')
        wrong = valid[:-1] + ('0' if valid[-1] != '0' else '1')
        self.assert_bad(wrong, "身份证号校验位错误")

    def test_birth_date_invalid_but_check_digit_ok(self):
        # 这些号码校验位都正确，专门验证出生日期分支
        self.assert_bad(make_id('52032519901301123'), "身份证号出生月份无效")  # 13 月
        self.assert_bad(make_id('52032519900001123'), "身份证号出生月份无效")  # 00 月
        self.assert_bad(make_id('52032519900230123'), "身份证号出生日期无效")  # 2 月 30 日
        self.assert_bad(make_id('52032519900229123'), "身份证号出生日期无效")  # 平年 2 月 29
        self.assert_bad(make_id('52032519900431123'), "身份证号出生日期无效")  # 4 月 31 日
        self.assert_bad(make_id('52032519900100123'), "身份证号出生日期无效")  # 0 日
        self.assert_bad(make_id('52032518000101123'), "身份证号出生年份无效")  # 1800 年
        self.assert_bad(make_id('52032520990101123'), "身份证号出生年份无效")  # 2099 年

    def test_empty_after_clean(self):
        # 空值判断发生在清洗之后：全空格、制表符、换行都算空
        self.assert_bad('', "身份证号不能为空")
        self.assert_bad(None, "身份证号不能为空")
        self.assert_bad('     ', "身份证号不能为空")
        self.assert_bad('\t\n ', "身份证号不能为空")

    def test_format_errors(self):
        self.assert_bad('52032519900101123A', "身份证号最后一位必须为数字或X")
        self.assert_bad('5203A5199001011234', "身份证号前17位必须为数字")
        self.assert_bad(make_id('52032519900101123')[:17], "身份证号必须为18位")
        self.assert_bad(make_id('52032519900101123') + '1', "身份证号必须为18位")

    def test_whitespace_tolerated(self):
        # 520325199001011235 的校验位已核对为 5，去掉空白后合法
        valid = '520325199001011235'
        self.assert_ok('  ' + valid + '  ')
        self.assert_ok('5203 2519 9001 0112 35')
        self.assert_ok(valid[:10] + '\t' + valid[10:])

    def test_lowercase_x_normalized(self):
        self.assert_ok('11010519491231002x')


class TestValidatePhone(unittest.TestCase):
    def test_empty_allowed(self):
        self.assertEqual(validate_phone(''), (True, ""))
        self.assertEqual(validate_phone(None), (True, ""))
        self.assertEqual(validate_phone('   '), (True, ""))
        self.assertEqual(validate_phone('\t\n'), (True, ""))

    def test_mobile_valid(self):
        for p in ('13800138000', '15012345678', '19912345678', '13456789012'):
            self.assertEqual(validate_phone(p), (True, ""), p)

    def test_mobile_invalid(self):
        for p in ('12345678901', '10012345678', '12800138000', '1380013800',
                  '138001380001', '123456789012', 'abcdefghijk', '02345678901'):
            self.assertEqual(validate_phone(p), (False, PHONE_ERR), p)

    def test_landline_rejected(self):
        # 清洗会剔掉横杠，但剔完仍不符合手机号规则，照样拒
        for p in ('010-12345678', '0755-87654321', '08511234567', '0851-12345678'):
            self.assertEqual(validate_phone(p), (False, PHONE_ERR), p)

    def test_whitespace_tolerated(self):
        self.assertEqual(validate_phone(' 13800138000 '), (True, ""))
        self.assertEqual(validate_phone('138 0013 8000'), (True, ""))
        self.assertEqual(validate_phone('138\t0013\t8000'), (True, ""))

    def test_hyphon_tolerated(self):
        # 口径变更：清洗阶段会剔除 "-"，号码本身合法就放行
        self.assertEqual(validate_phone('138-0013-8000'), (True, ""))


class TestCleanDigits(unittest.TestCase):
    def test_id_card_cleaning(self):
        self.assertEqual(clean_digits('5203 2519 9001 0112 35', True), '520325199001011235')
        self.assertEqual(clean_digits(' 520325199001011235 ', True), '520325199001011235')
        self.assertEqual(clean_digits('52032519900101123x', True), '52032519900101123X')
        self.assertEqual(clean_digits('520-325-199001011235', True), '520325199001011235')
        self.assertEqual(clean_digits('abc123', True), '123')

    def test_phone_cleaning(self):
        self.assertEqual(clean_digits(' 138 0013 8000 ', False), '13800138000')
        self.assertEqual(clean_digits('138-0013-8000', False), '13800138000')
        self.assertEqual(clean_digits('138 0013 8000', False), '13800138000')

    def test_x_not_allowed_for_phone(self):
        self.assertEqual(clean_digits('138X1380', False), '1381380')

    def test_none_input(self):
        self.assertEqual(clean_digits(None, True), '')
        self.assertEqual(clean_digits(None, False), '')


if __name__ == '__main__':
    unittest.main()
