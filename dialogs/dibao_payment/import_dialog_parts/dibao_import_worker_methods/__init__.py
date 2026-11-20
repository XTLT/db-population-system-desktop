from .._imports import *
from .._consts import *
from ..funcs import *

from ._attrs import DibaoImportWorkerAttrsMixin
from .m_init_mixin import DibaoImportWorkerMInitMixin
from .run_mixin import DibaoImportWorkerRunMixin

class DibaoImportWorker(DibaoImportWorkerMInitMixin, DibaoImportWorkerAttrsMixin, DibaoImportWorkerRunMixin, QThread):
    pass
