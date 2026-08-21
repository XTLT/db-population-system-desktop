from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.config import FONT_NAME, FONT_SIZE, BTN_SAVE_COLOR, BTN_CANCEL_COLOR
class RecoverDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("找回已删除人员")
        self.setMinimumSize(900, 500)
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("已删除人员列表（可选择恢复）")
        title.setFont(QFont(FONT_NAME, 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_recover = QPushButton("恢复选中人员")
        btn_recover.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 10px;")
        btn_recover.clicked.connect(self._recover)
        btn_close = QPushButton("关闭")
        btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 10px;")
        btn_close.clicked.connect(self.reject)
        btn_layout.addWidget(btn_recover)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

    def _load_data(self):
        from network.client import get_server_url
        if get_server_url():
            try:
                from network.client import api_deleted_persons
                deleted = api_deleted_persons()
                self._deleted_data = deleted
            except Exception:
                deleted = []
                self._deleted_data = []
        else:
            from core.database import get_deleted_persons
            deleted = get_deleted_persons()
            self._deleted_data = deleted

        headers = ["姓名", "身份证号", "户号", "与户主关系", "删除时间"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(deleted))

        for row_idx, p in enumerate(deleted):
            if isinstance(p, dict):
                values = [p.get('name', ''), p.get('id_card', ''), p.get('hu_hao', ''), p.get('relation', ''), p.get('deleted_at', '')]
            else:
                values = [p.name, p.id_card, p.hu_hao, p.relation, p.deleted_at]
            for col_idx, val in enumerate(values):
                item = QTableWidgetItem(str(val) if val else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _recover(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择要恢复的人员！")
            return

        name_item = self.table.item(row, 0)

        reply = QMessageBox.question(
            self, "确认恢复",
            f"确定要恢复人员 {name_item.text()} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from network.client import get_server_url
            if get_server_url():
                try:
                    from network.client import api_recover_person
                    deleted_data = self._deleted_data
                    if row < len(deleted_data):
                        deleted_id = deleted_data[row].get('id', '')
                        api_recover_person(deleted_id)
                        QMessageBox.information(self, "成功", f"已恢复人员 {name_item.text()}！")
                        self._load_data()
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"恢复失败：{str(e)}")
            else:
                from core.database import get_deleted_persons, recover_person
                deleted = get_deleted_persons()
                if row < len(deleted):
                    try:
                        recover_person(deleted[row].id)
                        QMessageBox.information(self, "成功", f"已恢复人员 {name_item.text()}！")
                        self._load_data()
                    except Exception as e:
                        QMessageBox.critical(self, "错误", f"恢复失败：{str(e)}")
