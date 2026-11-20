"""号码校验函数的统一调度出口。"""

from .clean_digits import clean_digits
from .install_digit_filter import install_digit_filter
from .validate_id_card import validate_id_card
from .validate_phone import validate_phone

__all__ = ['clean_digits', 'install_digit_filter', 'validate_id_card', 'validate_phone']
