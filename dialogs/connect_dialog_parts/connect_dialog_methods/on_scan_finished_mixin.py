from .._imports import *
from .._consts import *
from ..funcs import *

ServerScanner = None
get_recent_servers = None
save_recent_server = None

class ConnectDialogOnScanFinishedMixin:
    def _on_scan_finished(self):
        if not self.server_url:
            self.lbl_status.setText("未找到局域网服务器，请手动输入地址")
            self.lbl_status.setStyleSheet("color: #CC0000;")
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("🔍 自动搜索局域网服务器")
