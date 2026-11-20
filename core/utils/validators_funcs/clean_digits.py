"""号码清洗：把输入里的空格、横杠等非号码字符去掉。

用于身份证、电话号码这类编码字段，粘贴带空格的号码也能自动纠正。
"""


def clean_digits(text, allow_x=False):
    """把输入清洗成纯号码（允许的话保留 X/x 并转大写）。"""
    allowed = '0123456789Xx' if allow_x else '0123456789'
    cleaned = ''.join(ch for ch in (text or '') if ch in allowed)
    return cleaned.replace('x', 'X') if allow_x else cleaned
