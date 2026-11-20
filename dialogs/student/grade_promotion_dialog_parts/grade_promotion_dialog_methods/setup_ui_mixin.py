from .._imports import *
from .._consts import *
from ..funcs import *

GradePromotionWorker = None

class GradePromotionDialogSetupUiMixin:
    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("每年9月1日自动升年级")
        title.setFont(QFont(FONT_NAME, 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        mode_text = "（网络模式：服务器端执行）" if self.is_network else ""
        info = QLabel(
            f"将为所有在读学生自动升入下一个年级{mode_text}\n"
            "特殊升学：K3→G1、G9→G10、G12→U1、Z3→U3\n"
            "V3/J3/C3/Z3/U5/M3/D4 升级后标记为毕业\n"
            "标记为留级/休学/转学的学生不升年级"
        )
        info.setFont(QFont(FONT_NAME, FONT_SIZE))
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        btn_layout = QHBoxLayout()
        btn_promote = QPushButton("开始升年级")
        btn_promote.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 10px;")
        btn_promote.clicked.connect(self._promote)
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 10px;")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_promote)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
