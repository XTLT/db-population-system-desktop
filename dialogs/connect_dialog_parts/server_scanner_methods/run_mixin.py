from .._imports import *
from .._consts import *
from ..funcs import *



class ServerScannerRunMixin:
    def run(self):
        import socket
        import urllib.request
        import ssl

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        # 先检查本地
        local_addresses = ['127.0.0.1', 'localhost']
        for addr in local_addresses:
            for proto in ['https', 'http']:
                try:
                    url = f"{proto}://{addr}:5000/api/status"
                    urllib.request.urlopen(url, timeout=1, context=ctx if proto == 'https' else None)
                    self.found.emit(f"{proto}://127.0.0.1:5000")
                    return
                except Exception:
                    continue

        # 获取本机IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except Exception:
            self.finished_scan.emit()
            return

        # 扫描同网段
        base = ".".join(local_ip.split(".")[:3])

        for i in range(1, 255):
            ip = f"{base}.{i}"
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.15)
            result = sock.connect_ex((ip, 5000))
            sock.close()
            if result == 0:
                for proto in ['https', 'http']:
                    try:
                        url = f"{proto}://{ip}:5000/api/status"
                        urllib.request.urlopen(url, timeout=2, context=ctx if proto == 'https' else None)
                        self.found.emit(f"{proto}://{ip}:5000")
                        return
                    except Exception:
                        continue

        self.finished_scan.emit()
