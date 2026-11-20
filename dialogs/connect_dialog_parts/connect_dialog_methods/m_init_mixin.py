from .._imports import *
from .._consts import *
from ..funcs import *

ServerScanner = None
get_recent_servers = None
save_recent_server = None

class ConnectDialogMInitMixin:
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("连接服务器")
        self.setFixedSize(500, 280)
        self.server_url = None
        self._setup_ui()
