from .._imports import *
from .._consts import *
from ..funcs import *

import os
import re

_ADMIN_TOWNSHIP_SUFFIXES = ('街道', '镇', '乡')
_ADMIN_VILLAGE_SUFFIXES = ('社区', '村')


def _admin_core(text, suffixes):
    """去掉用户已填的行政后缀，用于和档案地址做前缀比对。"""
    value = str(text or '').strip()
    for suffix in suffixes:
        if value.endswith(suffix) and len(value) > len(suffix):
            return value[:-len(suffix)]
    return value


def _strip_admin_prefix(address, township, village):
    """从档案地址里剥掉已填的乡镇/村，避免打印成“云峰镇云峰镇五八组”。"""
    detail = str(address or '').strip()
    for value, suffixes in (
        (township, _ADMIN_TOWNSHIP_SUFFIXES),
        (village, _ADMIN_VILLAGE_SUFFIXES),
    ):
        core = _admin_core(value, suffixes)
        if core and detail.startswith(core):
            detail = detail[len(core):]
            for suffix in suffixes:
                if detail.startswith(suffix):
                    detail = detail[len(suffix):]
                    break
    return detail.lstrip(' \t　、,，-—')


def _split_admin_address(address):
    """把“云峰镇云峰村五八组”拆成乡镇、村、详细地址，仅用于弹窗预填。"""
    text = str(address or '').strip()
    township = ''
    village = ''
    match = re.match(r'(.{1,15}?(?:街道|镇|乡))', text)
    if match:
        township = match.group(1)
        text = text[len(township):]
    match = re.match(r'(.{1,12}?(?:社区|村))', text)
    if match:
        village = match.group(1)
        text = text[len(village):]
    return township, village, text.lstrip(' \t　、,，-—')


class _MeetingInfoDialog(QDialog):
    """单户 PDF 导出前：乡镇/村、档案详细地址和会议记录表头。"""

    def __init__(self, parent=None, address=''):
        super().__init__(parent)
        self.setWindowTitle("导出信息（乡/村、会议记录）")
        self.setMinimumWidth(560)
        self._mode = None
        township, village, detail = _split_admin_address(address)

        layout = QVBoxLayout(self)
        hint = QLabel(
            "“乡（镇、街道）/村（社区）”会写入承诺书、成员证明、一户一宅、相邻意见；"
            "详细地址自动接在村后。会议信息用于会议记录，留空则打印横线、打印后手填。"
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        form = QFormLayout()
        self.ed_township = QLineEdit()
        self.ed_township.setText(township)
        self.ed_township.setPlaceholderText("例：云峰镇；可直接写全称")
        self.ed_village = QLineEdit()
        self.ed_village.setText(village)
        self.ed_village.setPlaceholderText("例：云峰村；可直接写全称")
        self.ed_detail = QLineEdit()
        self.ed_detail.setText(detail)
        self.ed_detail.setReadOnly(True)
        self.ed_detail.setPlaceholderText("取自已保存的审批地址/户口所在地")
        form.addRow("乡（镇、街道）：", self.ed_township)
        form.addRow("村（社区）：", self.ed_village)
        form.addRow("档案详细地址：", self.ed_detail)
        form.addRow(QLabel(""))
        self.ed_date = QLineEdit()
        self.ed_date.setPlaceholderText("例：2026年11月23日")
        self.ed_place = QLineEdit()
        self.ed_place.setPlaceholderText("例：云峰组会议室")
        self.ed_host = QLineEdit()
        self.ed_host.setPlaceholderText("例：李某某")
        self.ed_recorder = QLineEdit()
        self.ed_recorder.setPlaceholderText("例：王某某")
        form.addRow("会议时间：", self.ed_date)
        form.addRow("会议地点：", self.ed_place)
        form.addRow("主持人：", self.ed_host)
        form.addRow("记录人：", self.ed_recorder)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        btn_ok = QPushButton("确定")
        btn_ok.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; padding: 8px;")
        btn_skip = QPushButton("跳过会议信息（保留乡/村）")
        btn_skip.setStyleSheet("padding: 8px;")
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px;")
        btn_ok.clicked.connect(lambda: self._finish('ok'))
        btn_skip.clicked.connect(lambda: self._finish('skip'))
        btn_cancel.clicked.connect(self.reject)
        buttons.addStretch()
        buttons.addWidget(btn_ok)
        buttons.addWidget(btn_skip)
        buttons.addWidget(btn_cancel)
        layout.addLayout(buttons)

    def _finish(self, mode):
        self._mode = mode
        self.accept()

    def values(self, mode=None):
        mode = mode or self._mode
        info = {
            'township': self.ed_township.text().strip(),
            'village': self.ed_village.text().strip(),
            'date': '',
            'place': '',
            'host': '',
            'recorder': '',
        }
        if mode != 'skip':
            info.update({
                'date': self.ed_date.text().strip(),
                'place': self.ed_place.text().strip(),
                'host': self.ed_host.text().strip(),
                'recorder': self.ed_recorder.text().strip(),
            })
        return info


def _ask_meeting_info(parent, address=''):
    dialog = _MeetingInfoDialog(parent, address=address)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    return dialog.values()


class _BatchMeetingDialog(QDialog):
    """批量导出前：勾选同一场会议的户，并录入会议记录表头。"""

    def __init__(self, parent=None, candidates=None, preselected_ids=None, address=''):
        super().__init__(parent)
        self.setWindowTitle("批量导出（会议记录/公示）")
        self.setMinimumSize(660, 700)
        self._mode = None
        self._candidates = list(candidates or [])
        preselected = set(preselected_ids or [])
        township, village, _ = _split_admin_address(address)

        layout = QVBoxLayout(self)
        hint = QLabel(
            "勾选本次同一场会议的户（2～50 户）。每户生成 6 页，"
            "最后共用 1 张《会议记录》和 1 张《公示》。"
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        addr_box = QGroupBox("本人申请在（本次导出共用抬头）")
        addr_row = QHBoxLayout(addr_box)
        self.ed_township = QLineEdit()
        self.ed_township.setText(township)
        self.ed_township.setPlaceholderText("例：云峰镇；可直接写全称")
        self.ed_village = QLineEdit()
        self.ed_village.setText(village)
        self.ed_village.setPlaceholderText("例：云峰村；可直接写全称")
        addr_row.addWidget(QLabel("乡（镇、街道）："))
        addr_row.addWidget(self.ed_township, 1)
        addr_row.addWidget(QLabel("村（社区）："))
        addr_row.addWidget(self.ed_village, 1)
        layout.addWidget(addr_box)

        top = QHBoxLayout()
        top.addWidget(QLabel("参会/公示户："))
        top.addStretch()
        btn_all = QPushButton("全选")
        btn_all.setStyleSheet("padding: 5px 12px;")
        btn_all.setToolTip("一次最多 50 户；超过时只勾选前 50 户")
        btn_none = QPushButton("清空")
        btn_none.setStyleSheet("padding: 5px 12px;")
        top.addWidget(btn_all)
        top.addWidget(btn_none)
        layout.addLayout(top)

        self.table = QTableWidget(len(self._candidates), 3)
        self.table.setHorizontalHeaderLabels(["选择", "申请编号", "申请人"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.verticalHeader().setVisible(False)
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 60)
        self.table.setMinimumHeight(220)
        self.table.setMaximumHeight(280)

        for row, cand in enumerate(self._candidates):
            check = QTableWidgetItem()
            check.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            check.setCheckState(
                Qt.CheckState.Checked if cand.get('id') in preselected else Qt.CheckState.Unchecked
            )
            check.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, check)

            no_item = QTableWidgetItem(str(cand.get('app_no', '')))
            no_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            name_item = QTableWidgetItem(str(cand.get('owner_name', '')))
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 1, no_item)
            self.table.setItem(row, 2, name_item)
        layout.addWidget(self.table)

        self.lbl_count = QLabel()
        layout.addWidget(self.lbl_count)

        form = QFormLayout()
        self.ed_date = QLineEdit()
        self.ed_date.setPlaceholderText("例：2026年11月23日")
        self.ed_place = QLineEdit()
        self.ed_place.setPlaceholderText("例：云峰组会议室")
        self.ed_host = QLineEdit()
        self.ed_host.setPlaceholderText("例：李某某")
        self.ed_recorder = QLineEdit()
        self.ed_recorder.setPlaceholderText("例：王某某")
        form.addRow("会议时间：", self.ed_date)
        form.addRow("会议地点：", self.ed_place)
        form.addRow("主持人：", self.ed_host)
        form.addRow("记录人：", self.ed_recorder)
        layout.addLayout(form)

        tip = QLabel("乡/村和会议信息都可留空；留空处 PDF 会打印横线，打印后手填。")
        tip.setWordWrap(True)
        tip.setStyleSheet("color: #666;")
        layout.addWidget(tip)

        buttons = QHBoxLayout()
        btn_ok = QPushButton("确定并导出")
        btn_ok.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; padding: 8px;")
        btn_skip = QPushButton("跳过会议信息（打印后手写）")
        btn_skip.setStyleSheet("padding: 8px;")
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px;")
        btn_ok.clicked.connect(lambda: self._finish('ok'))
        btn_skip.clicked.connect(lambda: self._finish('skip'))
        btn_cancel.clicked.connect(self.reject)
        buttons.addStretch()
        buttons.addWidget(btn_ok)
        buttons.addWidget(btn_skip)
        buttons.addWidget(btn_cancel)
        layout.addLayout(buttons)

        btn_all.clicked.connect(self._check_all)
        btn_none.clicked.connect(self._clear_all)
        self.table.itemChanged.connect(self._update_count)
        self._update_count()

    def selected_ids(self):
        ids = []
        for row, cand in enumerate(self._candidates):
            item = self.table.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                if cand.get('id'):
                    ids.append(cand['id'])
        return ids

    def _check_all(self):
        limit = min(self.table.rowCount(), 50)
        for row in range(limit):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(Qt.CheckState.Checked)

    def _clear_all(self):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(Qt.CheckState.Unchecked)

    def _update_count(self):
        n = len(self.selected_ids())
        self.lbl_count.setText("已勾选 %d 户（需 2～50 户）" % n)
        self.lbl_count.setStyleSheet("color: %s;" % ("#CC0000" if n < 2 or n > 50 else "#008800"))

    def _finish(self, mode):
        ids = self.selected_ids()
        if len(ids) < 2:
            QMessageBox.information(
                self, "提示",
                "请勾选至少两户。\n只导一户请关闭本窗口，回列表点“导出PDF”。",
            )
            return
        if len(ids) > 50:
            QMessageBox.information(self, "提示", "一次最多导出 50 户，请减少勾选。")
            return
        self._mode = mode
        self.accept()

    def values(self, mode=None):
        mode = mode or self._mode
        info = {
            'township': self.ed_township.text().strip(),
            'village': self.ed_village.text().strip(),
            'date': '',
            'place': '',
            'host': '',
            'recorder': '',
        }
        if mode != 'skip':
            info.update({
                'date': self.ed_date.text().strip(),
                'place': self.ed_place.text().strip(),
                'host': self.ed_host.text().strip(),
                'recorder': self.ed_recorder.text().strip(),
            })
        return info


def _ask_batch_export(parent, candidates, preselected_ids=None, address=''):
    dialog = _BatchMeetingDialog(
        parent, candidates, preselected_ids, address=address,
    )
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    return dialog.selected_ids(), dialog.values()


class HouseBuildListDialogDoExportMixin:
    def _do_batch_export(self, preselected_ids=None):
        candidates = [
            {
                'id': item.get('id'),
                'app_no': item.get('app_no', ''),
                'owner_name': item.get('owner_name', ''),
            }
            for item in self.items if item.get('id')
        ]
        if len(candidates) < 2:
            QMessageBox.information(
                self, "提示",
                "当前列表不足两户，无法批量导出。\n单户导出请点“导出PDF”。",
            )
            return

        row = self.table.currentRow()
        address = ''
        if 0 <= row < len(self.items):
            current = self.items[row]
            address = current.get('approval_address') or current.get('owner_hukou') or ''
        picked = _ask_batch_export(
            self, candidates, preselected_ids=preselected_ids, address=address,
        )
        if picked is None:
            return
        app_ids, meeting = picked

        default_name = '宅基地建房一户一档_%d户.pdf' % len(app_ids)
        path, _ = QFileDialog.getSaveFileName(
            self, "批量导出（多户合并）", default_name, 'PDF 文件 (*.pdf)',
        )
        if not path:
            return
        try:
            api_house_build_batch_download(app_ids, path, meeting=meeting)
        except Exception as e:
            QMessageBox.warning(self, "提示", f"批量导出失败：{e}")
            return
        if QMessageBox.question(
            self, "导出完成",
            "已将 %d 户合并为一个 PDF：\n每户 6 页（申请表、审批表、4 张一户表），"
            "最后共用 1 张会议记录和 1 张公示。\n\n已保存到：\n%s\n\n现在打开吗？"
            % (len(app_ids), path),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        ) == QMessageBox.StandardButton.Yes:
            try:
                os.startfile(path)
            except Exception:
                pass

    def _do_export(self, fmt):
        if not self.current_app_id:
            QMessageBox.information(self, "提示", "请先选择一条申请记录。")
            return
        row = self.table.currentRow()
        item = self.items[row] if 0 <= row < len(self.items) else {}
        name = item.get('owner_name', '')
        no = item.get('app_no', '')
        address = item.get('approval_address') or item.get('owner_hukou') or ''
        meeting = None
        if fmt == 'pdf':
            meeting = _ask_meeting_info(self, address=address)
            if meeting is None:
                return
        suffix = 'xlsx' if fmt == 'xlsx' else 'pdf'
        default_name = '宅基地建房申请_%s_%s.%s' % (name or '未命名', no or '', suffix)
        path, _ = QFileDialog.getSaveFileName(
            self, "保存导出文件", default_name,
            'Excel 文件 (*.xlsx)' if fmt == 'xlsx' else 'PDF 文件 (*.pdf)',
        )
        if not path:
            return
        try:
            api_house_build_download(self.current_app_id, fmt, path, meeting=meeting)
        except Exception as e:
            QMessageBox.warning(self, "提示", f"导出失败：{e}")
            return
        if QMessageBox.question(
            self, "导出完成", "已保存到：\n%s\n\n现在打开吗？" % path,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        ) == QMessageBox.StandardButton.Yes:
            try:
                os.startfile(path)
            except Exception:
                pass
