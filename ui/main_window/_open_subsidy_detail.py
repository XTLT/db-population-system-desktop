from PyQt6.QtWidgets import QHBoxLayout, QDialog, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.config import FONT_NAME


def _open_subsidy_detail(self, id_card: str, name: str):

    is_admin = self.current_user.get('role') == 'admin'

    dialog = QDialog(self)
    dialog.setWindowTitle("查看补贴")
    dialog.setFixedSize(300, 150)

    layout = QVBoxLayout(dialog)
    layout.setSpacing(10)
    layout.setContentsMargins(20, 20, 20, 20)

    title = QLabel(f"请选择补贴类型：{name}")
    title.setFont(QFont(FONT_NAME, 12))
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)

    btn_layout = QHBoxLayout()

    subsidy_types = [
        ("地力补贴", "land_subsidy"),
    ]

    for display_name, subsidy_key in subsidy_types:
        btn = QPushButton(display_name)
        btn.setFont(QFont(FONT_NAME, 11))
        btn.clicked.connect(lambda checked, key=subsidy_key: self._show_subsidy_dialog(key, id_card, name, is_admin, dialog))
        btn_layout.addWidget(btn)

    layout.addLayout(btn_layout)

    btn_close = QPushButton("关闭")
    btn_close.clicked.connect(dialog.close)
    layout.addWidget(btn_close)

    dialog.exec()
