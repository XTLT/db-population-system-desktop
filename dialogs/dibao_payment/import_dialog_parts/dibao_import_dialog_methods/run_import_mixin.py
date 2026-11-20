from .._imports import *
from .._consts import *
from ..funcs import *

DibaoImportWorker = None

class DibaoImportDialogRunImportMixin:
    def _run_import(self, dry_run):
        self.worker = DibaoImportWorker(self._file_path, self.is_network_mode, self._period, dry_run=dry_run)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()
