from .._imports import *
from .._consts import *
from ..funcs import *

TekunImportWorker = None

class TekunImportDialogOnProgressMixin:
    def _on_progress(self, value):
        self.progress_bar.setValue(value)
