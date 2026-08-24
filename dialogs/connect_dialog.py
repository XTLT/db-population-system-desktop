
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import json
import os

from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR, APPDATA_DIR


RECENT_SERVERS_FILE = os.path.join(APPDATA_DIR, "recent_servers.json")
MAX_RECENT_SERVERS = 5


def get_recent_servers():
    try:
        if os.path.exists(RECENT_SERVERS_FILE):
            with open(RECENT_SERVERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return []


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


class ServerScanner(QThread):
    found = pyqtSignal(str)
    finished_scan = pyqtSignal()

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


class ConnectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("连接服务器")
        self.setFixedSize(500, 280)
        self.server_url = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("连接到服务器")
        title.setFont(QFont(FONT_NAME, 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 自动搜索按钮
        self.btn_scan = QPushButton("🔍 自动搜索局域网服务器")
        self.btn_scan.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.btn_scan.setStyleSheet(f"""
            QPushButton {{
                background-color: #0078D4;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: #106EBE;
            }}
            QPushButton:disabled {{
                background-color: #999;
            }}
        """)
        self.btn_scan.clicked.connect(self._start_scan)
        layout.addWidget(self.btn_scan)

        # 扫描状态标签
        self.lbl_status = QLabel("")
        self.lbl_status.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("color: #666;")
        self.lbl_status.setVisible(False)
        layout.addWidget(self.lbl_status)

        # 分隔线
        separator = QLabel("─" * 20 + " 或 " + "─" * 20)
        separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        separator.setStyleSheet("color: #999;")
        layout.addWidget(separator)

        # 手动输入
        self.lbl_input = QLabel("输入服务器地址：")
        self.lbl_input.setFont(QFont(FONT_NAME, FONT_SIZE))
        layout.addWidget(self.lbl_input)

        self.cmb_server = QComboBox()
        self.cmb_server.setEditable(True)
        self.cmb_server.setPlaceholderText("https://服务器IP:端口 或 域名")
        self.cmb_server.setFont(QFont(FONT_NAME, FONT_SIZE))
        
        recent = get_recent_servers()
        if recent:
            self.cmb_server.addItems(recent)
        
        layout.addWidget(self.cmb_server)

        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_connect = QPushButton("连接")
        self.btn_connect.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.btn_connect.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 10px 30px;")
        self.btn_connect.clicked.connect(self._connect)
        btn_layout.addWidget(self.btn_connect)

        btn_local = QPushButton("本地模式")
        btn_local.setFont(QFont(FONT_NAME, FONT_SIZE))
        btn_local.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 10px 20px;")
        btn_local.clicked.connect(self._local_mode)
        btn_layout.addWidget(btn_local)

        layout.addLayout(btn_layout)

    def _start_scan(self):
        self.btn_scan.setEnabled(False)
        self.btn_scan.setText("正在搜索...")
        self.lbl_status.setVisible(True)
        self.lbl_status.setText("正在扫描局域网服务器...")
        self.lbl_status.setStyleSheet("color: #0078D4;")

        self.scanner = ServerScanner()
        self.scanner.found.connect(self._on_server_found)
        self.scanner.finished_scan.connect(self._on_scan_finished)
        self.scanner.start()

    def _on_server_found(self, url):
        self.server_url = url
        self.lbl_status.setText(f"✓ 已找到服务器：{url}")
        self.lbl_status.setStyleSheet("color: green; font-weight: bold;")
        self.cmb_server.setEditText(url)
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("🔍 自动搜索局域网服务器")

    def _on_scan_finished(self):
        if not self.server_url:
            self.lbl_status.setText("未找到局域网服务器，请手动输入地址")
            self.lbl_status.setStyleSheet("color: #CC0000;")
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("🔍 自动搜索局域网服务器")

    def get_server_url(self) -> str:
        return self.cmb_server.currentText().strip()

    def _connect(self):
        url = self.get_server_url()
        if not url:
            QMessageBox.warning(self, "提示", "请输入服务器地址！")
            return
        
        save_recent_server(url)
        self.accept()

    def _local_mode(self):
        self.cmb_server.setEditText("")
        self.accept()
