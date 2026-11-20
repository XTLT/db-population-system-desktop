from .._imports import *
from .._consts import *
from ..funcs import *



class LandSubsidyImportWorkerMInitMixin:
    def __init__(self, file_path: str, subsidy_year: str, is_network_mode: bool, dry_run: bool = False):
        super().__init__()
        self.file_path = file_path
        self.subsidy_year = subsidy_year
        self.is_network_mode = is_network_mode
        self.dry_run = dry_run
