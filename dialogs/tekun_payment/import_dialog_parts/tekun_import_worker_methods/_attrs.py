from .._imports import *
from .._consts import *
from ..funcs import *



class TekunImportWorkerAttrsMixin:
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
