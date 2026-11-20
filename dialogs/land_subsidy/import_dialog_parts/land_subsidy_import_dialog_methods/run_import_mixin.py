from .._imports import *
from .._consts import *
from ..funcs import *

LandSubsidyImportWorker = None

class LandSubsidyImportDialogRunImportMixin:
    def _run_import(self, dry_run):
        self.worker = LandSubsidyImportWorker(self._file_path, self._year, self.is_network_mode, dry_run=dry_run)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()
