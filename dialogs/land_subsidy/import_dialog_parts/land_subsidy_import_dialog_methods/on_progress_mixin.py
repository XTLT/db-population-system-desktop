from .._imports import *
from .._consts import *
from ..funcs import *

LandSubsidyImportWorker = None

class LandSubsidyImportDialogOnProgressMixin:
    def _on_progress(self, value):
        self.progress_bar.setValue(value)
