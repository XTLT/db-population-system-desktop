from .._imports import *
from .._consts import *
from ..funcs import *



class ServerScannerAttrsMixin:
    found = pyqtSignal(str)
    finished_scan = pyqtSignal()
