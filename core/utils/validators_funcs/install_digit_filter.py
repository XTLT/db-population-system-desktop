"""给 QLineEdit 挂即时清洗，非法字符一输入/一粘贴就被删掉。"""

from .clean_digits import clean_digits


def install_digit_filter(line_edit, allow_x=False):
    """用户看到的始终是干净号码，不会等到点保存才报错。"""
    def _clean(text):
        cleaned = clean_digits(text, allow_x)
        if cleaned != text:
            pos = line_edit.cursorPosition()
            line_edit.setText(cleaned)
            line_edit.setCursorPosition(min(pos, len(cleaned)))

    line_edit.textChanged.connect(_clean)
