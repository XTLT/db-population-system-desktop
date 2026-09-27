from PyQt6.QtWidgets import QLineEdit, QDialog, QLabel, QHBoxLayout, QMessageBox, QVBoxLayout, QFormLayout, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.config import FONT_NAME, BTN_SAVE_COLOR, BTN_CANCEL_COLOR


def _add_household(self):
    from core.database import generate_new_hu_hao, add_new_household

    dialog = QDialog(self)
    dialog.setWindowTitle("新增户")
    dialog.setFixedSize(400, 340)
    layout = QVBoxLayout(dialog)

    title = QLabel("新增户")
    title.setFont(QFont(FONT_NAME, 12, QFont.Weight.Bold))
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)

    form = QFormLayout()
    txt_huhao = QLineEdit()
    if self.is_network_mode:
        try:
            from network.client import api_new_hu_hao
            result = api_new_hu_hao()
            txt_huhao.setText(result.get('hu_hao', ''))
        except Exception:
            txt_huhao.setText('')
    else:
        txt_huhao.setText(generate_new_hu_hao())
    form.addRow("户号：", txt_huhao)
    txt_name = QLineEdit()
    txt_name.setPlaceholderText("户主姓名")
    form.addRow("户主姓名：", txt_name)
    txt_idcard = QLineEdit()
    txt_idcard.setPlaceholderText("身份证号")
    form.addRow("身份证号：", txt_idcard)
    txt_address = QLineEdit()
    form.addRow("地址：", txt_address)
    txt_phone = QLineEdit()
    form.addRow("电话：", txt_phone)
    txt_land = QLineEdit()
    txt_land.setPlaceholderText("亩")
    form.addRow("土地面积：", txt_land)
    txt_local_welfare_forest = QLineEdit()
    txt_local_welfare_forest.setPlaceholderText("亩")
    form.addRow("地方公益林：", txt_local_welfare_forest)
    txt_national_welfare_forest = QLineEdit()
    txt_national_welfare_forest.setPlaceholderText("亩")
    form.addRow("国家公益林：", txt_national_welfare_forest)
    txt_commercial_forest = QLineEdit()
    txt_commercial_forest.setPlaceholderText("亩")
    form.addRow("非国有天然商品林：", txt_commercial_forest)
    layout.addLayout(form)

    def do_add():
        if not txt_name.text().strip():
            QMessageBox.warning(dialog, "提示", "请输入户主姓名！")
            return
        if not txt_idcard.text().strip():
            QMessageBox.warning(dialog, "提示", "请输入身份证号！")
            return
        try:
            if self.is_network_mode:
                from network.client import api_add_household
                result = api_add_household({
                    'hu_hao': txt_huhao.text().strip(),
                    'name': txt_name.text().strip(),
                    'id_card': txt_idcard.text().strip(),
                    'address': txt_address.text().strip(),
                    'phone': txt_phone.text().strip(),
                    'land_area': txt_land.text().strip(),
                    'local_welfare_forest_area': txt_local_welfare_forest.text().strip(),
                    'national_welfare_forest_area': txt_national_welfare_forest.text().strip(),
                    'commercial_forest_area': txt_commercial_forest.text().strip()
                })
                if result.get('success'):
                    QMessageBox.information(dialog, "成功", f"新户 {txt_huhao.text()} 创建成功！")
                    dialog.accept()
                    self._do_search()
                else:
                    QMessageBox.critical(dialog, "错误", result.get('error', '创建失败'))
            else:
                add_new_household(
                    hu_hao=txt_huhao.text().strip(),
                    name=txt_name.text().strip(),
                    id_card=txt_idcard.text().strip(),
                    address=txt_address.text().strip(),
                    phone=txt_phone.text().strip(),
                    land_area=txt_land.text().strip(),
                    local_welfare_forest_area=txt_local_welfare_forest.text().strip(),
                    national_welfare_forest_area=txt_national_welfare_forest.text().strip(),
                    commercial_forest_area=txt_commercial_forest.text().strip()
                )
                QMessageBox.information(dialog, "成功", f"新户 {txt_huhao.text()} 创建成功！")
                dialog.accept()
                self._do_search()
        except Exception as e:
            QMessageBox.critical(dialog, "错误", str(e))

    btn_layout = QHBoxLayout()
    btn_ok = QPushButton("创建")
    btn_ok.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 8px;")
    btn_ok.clicked.connect(do_add)
    btn_cancel = QPushButton("取消")
    btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px;")
    btn_cancel.clicked.connect(dialog.reject)
    btn_layout.addWidget(btn_ok)
    btn_layout.addWidget(btn_cancel)
    layout.addLayout(btn_layout)

    dialog.exec()
