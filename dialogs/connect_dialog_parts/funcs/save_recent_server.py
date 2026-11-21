"""原模块的顶层函数 save_recent_server。"""
from .._imports import *
from .._consts import *
from .get_recent_servers import get_recent_servers

def save_recent_server(url):
    servers = get_recent_servers()
    if url in servers:
        servers.remove(url)
    servers.insert(0, url)
    servers = servers[:MAX_RECENT_SERVERS]
    try:
        os.makedirs(os.path.dirname(RECENT_SERVERS_FILE), exist_ok=True)
        with open(RECENT_SERVERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(servers, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
