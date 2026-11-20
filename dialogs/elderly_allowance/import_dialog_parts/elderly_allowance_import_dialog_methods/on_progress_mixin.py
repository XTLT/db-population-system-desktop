from .._imports import *
from .._consts import *
from ..funcs import *

ElderlyAllowanceImportWorker = None

class ElderlyAllowanceImportDialogOnProgressMixin:
    def _on_progress(self, value):
        self.progress_bar.setValue(value)
