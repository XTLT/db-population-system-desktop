from .._imports import *
from .._consts import *
from ..funcs import *

DisabilityCareImportWorker = None

class DisabilityCareImportDialogOnProgressMixin:
    def _on_progress(self, value):
        self.progress_bar.setValue(value)
