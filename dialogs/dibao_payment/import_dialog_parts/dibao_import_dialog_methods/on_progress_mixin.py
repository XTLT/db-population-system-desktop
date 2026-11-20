from .._imports import *
from .._consts import *
from ..funcs import *

DibaoImportWorker = None

class DibaoImportDialogOnProgressMixin:
    def _on_progress(self, value):
        self.progress_bar.setValue(value)
