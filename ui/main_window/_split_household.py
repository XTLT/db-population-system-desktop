from PyQt6.QtWidgets import QScrollArea, QDialog, QLabel, QHBoxLayout, QMessageBox, QCheckBox, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtGui import QFont
from core.config import FONT_NAME, BTN_SAVE_COLOR, BTN_CANCEL_COLOR


def _split_household(self):
    if not self.current_family:
        QMessageBox.warning(self, "提示", "请先查询并选择一个家庭！")
        return


    dialog = QDialog(self)
    dialog.setWindowTitle("分户")
    dialog.setFixedSize(450, 400)
    layout = QVBoxLayout(dialog)

    title = QLabel(f"选择要分出去的人员（当前户号：{self.current_hu_hao}）")
    title.setFont(QFont(FONT_NAME, 11, QFont.Weight.Bold))
    layout.addWidget(title)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    container = QWidget()
    cb_layout = QVBoxLayout(container)

    checkboxes = []
    for p in self.current_family:
        cb = QCheckBox(f"{p.name} ({p.id_card}) - {p.relation}")
        cb.person_id = p.id
        checkboxes.append(cb)
        cb_layout.addWidget(cb)

    scroll.setWidget(container)
    layout.addWidget(scroll)

    def do_split():
        selected = [cb.person_id for cb in checkboxes if cb.isChecked()]
        if not selected:
            QMessageBox.warning(dialog, "提示", "请选择要分户的人员！")
            return
        reply = QMessageBox.question(
            dialog, "确认分户",
            f"确定将 {len(selected)} 人分出为新户？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.is_network_mode:
                    from network.client import _request
                    result = _request('POST', '/api/household/split', {
                        'person_ids': selected
                    })
                    if result.get('success'):
                        QMessageBox.information(dialog, "成功", f"分户成功！新户号：{result['new_hu_hao']}")
                        dialog.accept()
                        self._do_search()
                    else:
                        QMessageBox.critical(dialog, "错误", result.get('error', '分户失败'))
                else:
                    from core.database import split_household
                    new_hu_hao = split_household(selected)
                    QMessageBox.information(dialog, "成功", f"分户成功！新户号：{new_hu_hao}")
                    dialog.accept()
                    self._do_search()
            except Exception as e:
                QMessageBox.critical(dialog, "错误", str(e))

    btn_layout = QHBoxLayout()
    btn_ok = QPushButton("确认分户")
    btn_ok.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 8px;")
    btn_ok.clicked.connect(do_split)
    btn_cancel = QPushButton("取消")
    btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px;")
    btn_cancel.clicked.connect(dialog.reject)
    btn_layout.addWidget(btn_ok)
    btn_layout.addWidget(btn_cancel)
    layout.addLayout(btn_layout)

    dialog.exec()
