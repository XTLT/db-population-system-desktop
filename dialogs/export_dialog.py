from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QFormLayout, QGroupBox, QCheckBox,
    QScrollArea, QWidget, QGridLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal, QEvent

from core.config import FONT_NAME, FONT_SIZE


class CheckableComboBox(QWidget):
    selectionChanged = pyqtSignal()

    def __init__(self, items, parent=None):
        super().__init__(parent)
        self._items = items
        self._selected = []
        self._popup_visible = False

        self._btn = QPushButton("全部")
        self._btn.setStyleSheet(
            "QPushButton { text-align: left; padding: 4px 8px; border: 1px solid #ccc; "
            "background: white; } QPushButton:hover { border: 1px solid #999; }"
        )
        self._btn.setFixedHeight(28)
        self._btn.clicked.connect(self._toggle_popup)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._btn)

        self._popup = QWidget(self, Qt.WindowType.Popup)
        self._popup.setFixedWidth(220)
        popup_lay = QVBoxLayout(self._popup)
        popup_lay.setContentsMargins(4, 4, 4, 4)
        popup_lay.setSpacing(2)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(min(len(items) * 26 + 30, 180))
        container = QWidget()
        self._grid = QGridLayout(container)
        self._grid.setSpacing(2)
        self._grid.setContentsMargins(0, 0, 0, 0)

        self._suppress = False
        self._checkboxes = []

        cb_all = QCheckBox("全部")
        cb_all.setChecked(True)
        cb_all.stateChanged.connect(self._on_all_changed)
        self._grid.addWidget(cb_all, 0, 0)
        self._checkboxes.append(("全部", cb_all))

        cols = 2
        for idx, text in enumerate(items):
            cb = QCheckBox(text)
            cb.stateChanged.connect(self._on_item_changed)
            row = (idx + 1) // cols + 0
            col = (idx + 1) % cols
            self._grid.addWidget(cb, row, col)
            self._checkboxes.append((text, cb))

        scroll.setWidget(container)
        popup_lay.addWidget(scroll)

    def _toggle_popup(self):
        if self._popup_visible:
            self._popup.hide()
            self._popup_visible = False
        else:
            pos = self._btn.mapToGlobal(self._btn.rect().bottomLeft())
            self._popup.move(pos)
            self._popup.show()
            self._popup_visible = True

    def eventFilter(self, obj, event):
        if obj == self._popup and event.type() == QEvent.Type.MouseButtonPress:
            if not self._popup.geometry().contains(event.globalPosition().toPoint()):
                self._popup.hide()
                self._popup_visible = False
        return super().eventFilter(obj, event)

    def _on_all_changed(self, state):
        if self._suppress:
            return
        self._suppress = True
        checked = state == 2
        for text, cb in self._checkboxes:
            if text != "全部":
                cb.setChecked(checked)
        self._suppress = False
        self._update_button()
        self.selectionChanged.emit()

    def _on_item_changed(self, state):
        if self._suppress:
            return
        self._suppress = True
        all_checked = all(
            cb.isChecked() for text, cb in self._checkboxes if text != "全部"
        )
        self._checkboxes[0][1].setChecked(all_checked)
        self._suppress = False
        self._update_button()
        self.selectionChanged.emit()

    def _update_button(self):
        selected = self.get_selected()
        if not selected:
            self._btn.setText("全部")
        elif len(selected) <= 2:
            self._btn.setText("、".join(selected))
        else:
            self._btn.setText(f"{selected[0]}、{selected[1]}等{len(selected)}项")

    def get_selected(self):
        if self._checkboxes[0][1].isChecked():
            return []
        return [text for text, cb in self._checkboxes if text != "全部" and cb.isChecked()]

    def reset_selection(self):
        self._suppress = True
        self._checkboxes[0][1].setChecked(True)
        for text, cb in self._checkboxes:
            if text != "全部":
                cb.setChecked(False)
        self._suppress = False
        self._update_button()


class ExportFilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("数据筛选导出")
        self.setFixedSize(520, 440)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        filter_group = QGroupBox("筛选条件")
        filter_group.setFont(QFont(FONT_NAME, FONT_SIZE))
        form = QFormLayout()
        form.setSpacing(6)

        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("模糊匹配，留空不限")
        form.addRow("姓名：", self.txt_name)

        self.txt_address = QLineEdit()
        self.txt_address.setPlaceholderText("模糊匹配，留空不限")
        form.addRow("地址：", self.txt_address)

        age_layout = QHBoxLayout()
        self.txt_age_min = QLineEdit()
        self.txt_age_min.setPlaceholderText("最小")
        self.txt_age_min.setMaximumWidth(80)
        self.txt_age_max = QLineEdit()
        self.txt_age_max.setPlaceholderText("最大")
        self.txt_age_max.setMaximumWidth(80)
        age_layout.addWidget(self.txt_age_min)
        age_layout.addWidget(QLabel("~"))
        age_layout.addWidget(self.txt_age_max)
        age_layout.addStretch()
        form.addRow("年龄段：", age_layout)

        self.cmb_is_dead = QComboBox()
        self.cmb_is_dead.addItems(["全部", "否", "是"])
        form.addRow("是否死亡：", self.cmb_is_dead)

        self.cmb_relation = CheckableComboBox([
            "户主", "配偶", "子女", "父母", "兄弟姐妹",
            "祖父母", "孙子女", "儿媳", "女婿", "公婆", "岳父母",
            "孙媳", "孙婿", "其他"
        ])
        form.addRow("与户主关系：", self.cmb_relation)

        self.cmb_disability = CheckableComboBox([
            "肢体残疾", "视力残疾", "听力残疾",
            "智力残疾", "精神残疾", "多重残疾"
        ])
        form.addRow("残疾类别：", self.cmb_disability)

        self.cmb_dis_level = CheckableComboBox(["一级", "二级", "三级", "四级"])
        form.addRow("残疾等级：", self.cmb_dis_level)

        self.cmb_poor_type = CheckableComboBox([
            "脱贫户", "脱贫不稳定户",
            "边缘易致贫户", "突发严重困难户"
        ])
        form.addRow("脱贫户类型：", self.cmb_poor_type)

        self.cmb_dibao = QComboBox()
        self.cmb_dibao.addItems(["全部", "是", "否", "低保边缘家庭", "特困家庭"])
        form.addRow("低保：", self.cmb_dibao)

        self.cmb_jisheng = QComboBox()
        self.cmb_jisheng.addItems(["全部", "否", "是"])
        form.addRow("计生家庭：", self.cmb_jisheng)

        self.cmb_tekun = QComboBox()
        self.cmb_tekun.addItems(["全部", "是", "否"])
        form.addRow("特困供养：", self.cmb_tekun)

        self.cmb_tekun_type = CheckableComboBox(["集中供养", "散居特困"])
        form.addRow("供养类型：", self.cmb_tekun_type)

        self.cmb_land = QComboBox()
        self.cmb_land.addItems(["全部", "不为0", "空白"])
        form.addRow("土地面积：", self.cmb_land)

        filter_group.setLayout(form)
        layout.addWidget(filter_group)

        self.lbl_count = QLabel("当前符合条件：计算中...")
        self.lbl_count.setFont(QFont(FONT_NAME, FONT_SIZE))
        layout.addWidget(self.lbl_count)

        btn_layout = QHBoxLayout()
        btn_reset = QPushButton("重置筛选")
        btn_reset.clicked.connect(self._reset_filters)
        btn_export = QPushButton("导出")
        btn_export.setStyleSheet("background-color: #0078D4; color: white; font-weight: bold; padding: 8px 24px;")
        btn_export.clicked.connect(self.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_reset)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_export)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def _reset_filters(self):
        self.txt_name.clear()
        self.txt_address.clear()
        self.txt_age_min.clear()
        self.txt_age_max.clear()
        self.cmb_is_dead.setCurrentIndex(0)
        self.cmb_relation.reset_selection()
        self.cmb_disability.reset_selection()
        self.cmb_dis_level.reset_selection()
        self.cmb_poor_type.reset_selection()
        self.cmb_dibao.setCurrentIndex(0)
        self.cmb_jisheng.setCurrentIndex(0)
        self.cmb_tekun.setCurrentIndex(0)
        self.cmb_tekun_type.reset_selection()
        self.cmb_land.setCurrentIndex(0)

    def update_count(self, count: int):
        self.lbl_count.setText(f"当前符合条件：共 {count} 条记录")

    def get_filters(self) -> dict:
        return {
            "name": self.txt_name.text().strip(),
            "address": self.txt_address.text().strip(),
            "age_min": self.txt_age_min.text().strip(),
            "age_max": self.txt_age_max.text().strip(),
            "is_dead": self.cmb_is_dead.currentText(),
            "relation": self.cmb_relation.get_selected(),
            "disability": self.cmb_disability.get_selected(),
            "dis_level": self.cmb_dis_level.get_selected(),
            "poor_type": self.cmb_poor_type.get_selected(),
            "dibao": self.cmb_dibao.currentText(),
            "jisheng": self.cmb_jisheng.currentText(),
            "tekun": self.cmb_tekun.currentText(),
            "tekun_type": self.cmb_tekun_type.get_selected(),
            "land_area": self.cmb_land.currentText(),
        }
