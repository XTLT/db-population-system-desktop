from .._imports import *
from .._consts import *
from ..funcs import *



class ElderlyAllowanceImportWorkerMInitMixin:
    def __init__(self, file_path: str, is_network_mode: bool, period: str = "", dry_run: bool = False):
        super().__init__()
        self.file_path = file_path
        self.is_network_mode = is_network_mode
        self.dry_run = dry_run
        self.period = period
