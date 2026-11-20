from .._imports import *
from .._consts import *
from ..funcs import *

ServerScanner = None
get_recent_servers = None
save_recent_server = None

class ConnectDialogGetServerUrlMixin:
    def get_server_url(self) -> str:
        return self.cmb_server.currentText().strip()
