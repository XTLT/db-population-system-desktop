from .._imports import *
from .._consts import *
from ..funcs import *

PensionInsuranceImportWorker = None

class PensionInsuranceImportDialogOnProgressMixin:
    def _on_progress(self, value):
        self.progress_bar.setValue(value)
