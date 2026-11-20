from .._imports import *
from .._consts import *
from ..funcs import *



class ImportWorkerRunMixin:
    def run(self):
        try:
            if self.mode == "full":
                result = import_excel_full(self.file_path, self.progress.emit)
            else:
                result = import_excel_incremental(self.file_path, self.progress.emit)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
