"""常量与工具函数。"""


def fmt_area(value):
    try:
        num = float(value or 0)
    except (TypeError, ValueError):
        return ''
    if num <= 0:
        return ''
    return ('%.2f' % num).rstrip('0').rstrip('.')
