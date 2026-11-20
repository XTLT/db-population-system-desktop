from .._imports import *
from .._consts import *
from ..funcs import *

from ._attrs import TekunImportWorkerAttrsMixin
from .m_init_mixin import TekunImportWorkerMInitMixin
from .run_mixin import TekunImportWorkerRunMixin

class TekunImportWorker(TekunImportWorkerMInitMixin, TekunImportWorkerAttrsMixin, TekunImportWorkerRunMixin, QThread):
    pass
