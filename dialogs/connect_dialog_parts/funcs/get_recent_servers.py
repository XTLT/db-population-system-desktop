"""原模块的顶层函数 get_recent_servers。"""
from .._imports import *
from .._consts import *

def get_recent_servers():
    try:
        if os.path.exists(RECENT_SERVERS_FILE):
            with open(RECENT_SERVERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return []
