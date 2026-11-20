from .._imports import *
from .._consts import *
from ..funcs import *

ServerScanner = None
get_recent_servers = None
save_recent_server = None

class ConnectDialogLocalModeMixin:
    def _local_mode(self):
        self.cmb_server.setEditText("")
        self.accept()
