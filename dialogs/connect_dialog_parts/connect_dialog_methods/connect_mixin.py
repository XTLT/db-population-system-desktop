from .._imports import *
from .._consts import *
from ..funcs import *

ServerScanner = None
get_recent_servers = None
save_recent_server = None

class ConnectDialogConnectMixin:
    def _connect(self):
        url = self.get_server_url()
        if not url:
            QMessageBox.warning(self, "提示", "请输入服务器地址！")
            return
        
        save_recent_server(url)
        self.accept()
