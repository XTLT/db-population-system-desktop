from .._imports import *
from .._consts import *
from ..funcs import *

from ._attrs import ElderlyAllowanceImportWorkerAttrsMixin
from .m_init_mixin import ElderlyAllowanceImportWorkerMInitMixin
from .run_mixin import ElderlyAllowanceImportWorkerRunMixin

class ElderlyAllowanceImportWorker(ElderlyAllowanceImportWorkerMInitMixin, ElderlyAllowanceImportWorkerAttrsMixin, ElderlyAllowanceImportWorkerRunMixin, QThread):
    pass
