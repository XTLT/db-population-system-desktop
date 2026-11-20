from .._imports import *
from .._consts import *
from ..funcs import *

ServerScanner = None
get_recent_servers = None
save_recent_server = None

class ConnectDialogOnServerFoundMixin:
    def _on_server_found(self, url):
        self.server_url = url
        self.lbl_status.setText(f"✓ 已找到服务器：{url}")
        self.lbl_status.setStyleSheet("color: green; font-weight: bold;")
        self.cmb_server.setEditText(url)
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("🔍 自动搜索局域网服务器")
