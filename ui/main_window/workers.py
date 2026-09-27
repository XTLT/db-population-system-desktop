from PyQt6.QtCore import QThread, pyqtSignal
from network.update_checker import download_update


class DownloadWorker(QThread):
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(str, str)

    def __init__(self, version_info):
        super().__init__()
        self.version_info = version_info

    def run(self):
        def on_progress(downloaded, total):
            self.progress.emit(downloaded, total)

        filepath, error = download_update(self.version_info, progress_callback=on_progress)
        self.finished.emit(filepath or "", error)


class VersionCheckWorker(QThread):
    finished = pyqtSignal(object, str)

    def run(self):
        try:
            from network.update_checker import check_update
            result, error = check_update("desktop")
            self.finished.emit(result, error)
        except Exception as e:
            self.finished.emit(None, str(e))
