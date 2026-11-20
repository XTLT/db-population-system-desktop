from .._imports import *
from .._consts import *
from ..funcs import *

from ._attrs import PensionInsuranceImportWorkerAttrsMixin
from .m_init_mixin import PensionInsuranceImportWorkerMInitMixin
from .run_mixin import PensionInsuranceImportWorkerRunMixin

class PensionInsuranceImportWorker(PensionInsuranceImportWorkerMInitMixin, PensionInsuranceImportWorkerAttrsMixin, PensionInsuranceImportWorkerRunMixin, QThread):
    pass
