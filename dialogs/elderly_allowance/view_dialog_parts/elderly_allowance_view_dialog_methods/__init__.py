from .._imports import *
from .._consts import *
from ..funcs import *

from .m_init_mixin import ElderlyAllowanceViewDialogMInitMixin
from .setup_ui_mixin import ElderlyAllowanceViewDialogSetupUiMixin
from .load_data_mixin import ElderlyAllowanceViewDialogLoadDataMixin
from .do_delete_mixin import ElderlyAllowanceViewDialogDoDeleteMixin
from .do_export_mixin import ElderlyAllowanceViewDialogDoExportMixin

class ElderlyAllowanceViewDialog(ElderlyAllowanceViewDialogMInitMixin, ElderlyAllowanceViewDialogSetupUiMixin, ElderlyAllowanceViewDialogLoadDataMixin, ElderlyAllowanceViewDialogDoDeleteMixin, ElderlyAllowanceViewDialogDoExportMixin, QDialog):
    pass
