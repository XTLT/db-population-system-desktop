from .._imports import *
from .._consts import *
from ..funcs import *



class ImportWorkerMInitMixin:
    def __init__(self, file_path: str, mode: str):
        super().__init__()
        self.file_path = file_path
        self.mode = mode
