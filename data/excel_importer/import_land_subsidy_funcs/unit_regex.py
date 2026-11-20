"""列名单位括号匹配规则，如 （亩）/(元/亩)/(元)。"""

import re

UNIT_RE = re.compile(r"[（(][^）)]*[）)]")

# 兼容旧代码里的私有名
_UNIT_RE = UNIT_RE
