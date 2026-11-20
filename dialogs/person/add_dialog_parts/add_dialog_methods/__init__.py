from .._imports import *
from .._consts import *
from ..funcs import *

from .m_init_mixin import AddDialogMInitMixin
from .auto_fill_address_mixin import AddDialogAutoFillAddressMixin
from .setup_ui_mixin import AddDialogSetupUiMixin
from .on_id_card_changed_mixin import AddDialogOnIdCardChangedMixin
from .on_is_dead_changed_mixin import AddDialogOnIsDeadChangedMixin
from .death_date_value_mixin import AddDialogDeathDateValueMixin
from .on_disability_changed_mixin import AddDialogOnDisabilityChangedMixin
from .on_tekun_changed_mixin import AddDialogOnTekunChangedMixin
from .save_mixin import AddDialogSaveMixin

class AddDialog(AddDialogMInitMixin, AddDialogAutoFillAddressMixin, AddDialogSetupUiMixin, AddDialogOnIdCardChangedMixin, AddDialogOnIsDeadChangedMixin, AddDialogDeathDateValueMixin, AddDialogOnDisabilityChangedMixin, AddDialogOnTekunChangedMixin, AddDialogSaveMixin, QDialog):
    pass
