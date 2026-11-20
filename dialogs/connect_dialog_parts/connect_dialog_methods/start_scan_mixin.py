from .._imports import *
from .._consts import *
from ..funcs import *

ServerScanner = None
get_recent_servers = None
save_recent_server = None

class ConnectDialogStartScanMixin:
    def _start_scan(self):
        self.btn_scan.setEnabled(False)
        self.btn_scan.setText("正在搜索...")
        self.lbl_status.setVisible(True)
        self.lbl_status.setText("正在扫描局域网服务器...")
        self.lbl_status.setStyleSheet("color: #0078D4;")

        self.scanner = ServerScanner()
        self.scanner.found.connect(self._on_server_found)
        self.scanner.finished_scan.connect(self._on_scan_finished)
        self.scanner.start()
