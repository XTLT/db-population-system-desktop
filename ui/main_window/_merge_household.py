from PyQt6.QtWidgets import QScrollArea, QLineEdit, QDialog, QLabel, QHBoxLayout, QMessageBox, QCheckBox, QVBoxLayout, QWidget, QFormLayout, QPushButton
from PyQt6.QtGui import QFont
from core.config import FONT_NAME, BTN_SAVE_COLOR, BTN_CANCEL_COLOR


def _merge_household(self):
    if not self.current_family:
        QMessageBox.warning(self, "提示", "请先查询并选择一个家庭！")
        return


    dialog = QDialog(self)
    dialog.setWindowTitle("合户")
    dialog.setFixedSize(450, 450)
    layout = QVBoxLayout(dialog)

    title = QLabel(f"合户操作（当前户号：{self.current_hu_hao}）")
    title.setFont(QFont(FONT_NAME, 11, QFont.Weight.Bold))
    layout.addWidget(title)

    form = QFormLayout()
    txt_target = QLineEdit()
    txt_target.setPlaceholderText("目标户号（合并到此户）")
    txt_target.setText(self.current_hu_hao or "")
    form.addRow("目标户号：", txt_target)
    layout.addLayout(form)

    info = QLabel("选择要合并的人员：")
    layout.addWidget(info)

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

    def do_merge():
        target = txt_target.text().strip()
        if not target:
            QMessageBox.warning(dialog, "提示", "请输入目标户号！")
            return
        selected = [cb.person_id for cb in checkboxes if cb.isChecked()]
        if not selected:
            QMessageBox.warning(dialog, "提示", "请选择要合并的人员！")
            return
        reply = QMessageBox.question(
            dialog, "确认合户",
            f"确定将 {len(selected)} 人合并到户号 {target}？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.is_network_mode:
                    from network.client import _request
                    result = _request('POST', '/api/household/merge', {
                        'target_hu_hao': target,
                        'person_ids': selected
                    })
                    if result.get('success'):
                        QMessageBox.information(dialog, "成功", "合户成功！")
                        dialog.accept()
                        self._do_search()
                    else:
                        QMessageBox.critical(dialog, "错误", result.get('error', '合户失败'))
                else:
                    from core.database import merge_household
                    merge_household(target, selected)
                    QMessageBox.information(dialog, "成功", "合户成功！")
                    dialog.accept()
                    self._do_search()
            except Exception as e:
                QMessageBox.critical(dialog, "错误", str(e))

    btn_layout = QHBoxLayout()
    btn_ok = QPushButton("确认合户")
    btn_ok.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 8px;")
    btn_ok.clicked.connect(do_merge)
    btn_cancel = QPushButton("取消")
    btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px;")
    btn_cancel.clicked.connect(dialog.reject)
    btn_layout.addWidget(btn_ok)
    btn_layout.addWidget(btn_cancel)
    layout.addLayout(btn_layout)

    dialog.exec()
