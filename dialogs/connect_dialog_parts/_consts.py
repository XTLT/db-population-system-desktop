"""原模块的模块级常量。"""
from ._imports import *

RECENT_SERVERS_FILE = os.path.join(APPDATA_DIR, "recent_servers.json")

MAX_RECENT_SERVERS = 5

__all__ = ['RECENT_SERVERS_FILE', 'MAX_RECENT_SERVERS']
