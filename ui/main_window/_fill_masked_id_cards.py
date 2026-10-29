import os
from PyQt6.QtWidgets import (
    QProgressDialog, QDialog, QMessageBox, QFileDialog, QApplication,
    QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt


class _ColumnSelectDialog(QDialog):
    """选择 Sheet / 姓名列 / 证件号码列"""

    ID_COLS = ('身份证号', '证件号码', '身份证', '身份证号码', 'ID')
    NAME_COLS = ('姓名', '成员姓名', '户主姓名', '姓名（户主）', '姓名(户主)')

    def __init__(self, wb, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择补全列")
        self._wb = wb
        layout = QVBoxLayout(self)

        # Sheet 选择
        row_sheet = QHBoxLayout()
        row_sheet.addWidget(QLabel("工作表:"))
        self.cb_sheet = QComboBox(self)
        row_sheet.addWidget(self.cb_sheet, 1)
        layout.addLayout(row_sheet)

        # 姓名列
        row_name = QHBoxLayout()
        row_name.addWidget(QLabel("姓名列:"))
        self.cb_name = QComboBox(self)
        row_name.addWidget(self.cb_name, 1)
        layout.addLayout(row_name)

        # 证件号码列
        row_id = QHBoxLayout()
        row_id.addWidget(QLabel("证件号码列:"))
        self.cb_id = QComboBox(self)
        row_id.addWidget(self.cb_id, 1)
        layout.addLayout(row_id)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        for ws in wb.worksheets:
            self.cb_sheet.addItem(ws.title)
        self.cb_sheet.currentTextChanged.connect(self._load_columns)
        self._load_columns(self.cb_sheet.currentText())

    def _load_columns(self, sheet_name):
        ws = self._wb[sheet_name]
        headers = []
        for cell in ws[1]:
            v = str(cell.value or '').strip()
            if v and v not in headers:
                headers.append(v)
        self.cb_name.clear()
        self.cb_id.clear()
        self.cb_name.addItem("（未找到姓名列）") if not headers else None
        self.cb_id.addItem("（未找到证件号码列）") if not headers else None
        for h in headers:
            self.cb_name.addItem(h)
            self.cb_id.addItem(h)
        # 自动预选匹配的表头
        for i, h in enumerate(headers):
            if h in self.NAME_COLS:
                self.cb_name.setCurrentIndex(i)
            if h in self.ID_COLS:
                self.cb_id.setCurrentIndex(i)

    @property
    def sheet_name(self):
        return self.cb_sheet.currentText()

    @property
    def name_col(self):
        return self.cb_name.currentText()

    @property
    def id_col(self):
        return self.cb_id.currentText()


def _fill_masked_id_cards(self):
    """用系统中已有人员的完整身份证，补全Excel中脱敏的证件号码（前12位+******）。

    规则：证件号码含 * 视为脱敏号，取第一个 * 前的真实部分（前12位）与该行姓名
    在系统中唯一匹配（同名同前缀多人无法确定），成功则写回完整号码，其余列不变；
    无匹配或多匹配的保留原样并在结果中列出。
    """
    path, _ = QFileDialog.getOpenFileName(
        self, "选择需要补全证件号码的Excel文件", "",
        "Excel文件 (*.xlsx)"
    )
    if not path:
        return

    try:
        import openpyxl
        wb = openpyxl.load_workbook(path)
    except Exception as e:
        QMessageBox.critical(self, "错误", f"读取Excel文件失败：{e}")
        return

    dlg = _ColumnSelectDialog(wb, self)
    if dlg.exec() != QDialog.DialogCode.Accepted:
        return
    if not dlg.name_col or not dlg.id_col or dlg.name_col.startswith("（") or dlg.id_col.startswith("（"):
        QMessageBox.warning(self, "提示", "请正确选择姓名列和证件号码列")
        return

    ws = wb[dlg.sheet_name]
    headers = [str(c.value or '').strip() for c in ws[1]]
    name_idx = headers.index(dlg.name_col) + 1
    id_idx = headers.index(dlg.id_col) + 1

    # 一次性加载全部人员到内存
    progress = QProgressDialog("正在加载系统人员数据...", "取消", 0, 0, self)
    progress.setWindowTitle("补全证件号码")
    progress.setWindowModality(Qt.WindowModality.WindowModal)
    progress.setMinimumDuration(0)
    QApplication.processEvents()

    all_persons = []
    from network.client import get_server_url
    if get_server_url():
        from network.client import api_persons_lookup_all
        try:
            all_persons = api_persons_lookup_all()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载服务器数据失败：{e}")
            return
    else:
        from core.database import get_session, Person
        person_fields = [c.key for c in Person.__table__.columns if c.key != 'id']
        session = get_session()
        try:
            for p in session.query(Person).all():
                all_persons.append({f: (getattr(p, f) or '') for f in person_fields})
        finally:
            session.close()

    progress.cancel()

    if not all_persons:
        QMessageBox.warning(self, "提示", "系统中没有人员数据")
        return

    # 索引：姓名 -> [(person, id_card_prefix12)]；prefix12 -> {id_card: person}（配合姓名过滤）
    name_prefix_index = {}
    for p in all_persons:
        name = (p.get('name') or '').strip()
        idc = (p.get('id_card') or '').strip()
        if name and idc and len(idc) >= 12:
            name_prefix_index.setdefault(name, []).append(p)

    total = ws.max_row - 1
    if total <= 0:
        QMessageBox.warning(self, "提示", "文件中没有数据行")
        return

    progress = QProgressDialog("正在补全...", "取消", 0, total, self)
    progress.setWindowTitle("补全进度")
    progress.setWindowModality(Qt.WindowModality.WindowModal)
    progress.setMinimumDuration(0)

    filled = 0
    kept = 0
    details = []
    for row_idx in range(2, ws.max_row + 1):
        if progress.wasCanceled():
            break
        id_cell = ws.cell(row_idx, id_idx)
        id_val = str(id_cell.value or '').strip()
        if '*' not in id_val:
            progress.setValue(row_idx - 1)
            continue

        name = str(ws.cell(row_idx, name_idx).value or '').strip()
        prefix = id_val.split('*')[0].strip()
        if len(prefix) < 12:
            details.append(f"第{row_idx}行 {name}：脱敏号真实部分不足12位，保留")
            kept += 1
            progress.setValue(row_idx - 1)
            continue

        cands = [p for p in name_prefix_index.get(name, []) if (p.get('id_card') or '').startswith(prefix)]
        if len(cands) == 1:
            id_cell.value = cands[0]['id_card']
            filled += 1
        elif len(cands) == 0:
            details.append(f"第{row_idx}行 {name} {id_val}：系统中无此人，保留")
            kept += 1
        else:
            details.append(f"第{row_idx}行 {name} {id_val}：同名同前缀{len(cands)}人，无法确定，保留")
            kept += 1
        progress.setLabelText(f"第 {row_idx - 1}/{total} 行: {name}")
        progress.setValue(row_idx - 1)

    progress.setValue(total)

    if filled == 0 and kept == 0:
        QMessageBox.information(self, "提示", "文件中没有检测到脱敏证件号码（含*）")
        return

    default_name = os.path.splitext(os.path.basename(path))[0] + "_已补全.xlsx"
    save_path, _ = QFileDialog.getSaveFileName(
        self, "保存补全后的文件", default_name,
        "Excel文件 (*.xlsx)",
        options=QFileDialog.Option.DontUseNativeDialog
    )
    if not save_path:
        return

    try:
        wb.save(save_path)
    except Exception as e:
        QMessageBox.critical(self, "保存失败", f"文件保存失败：{e}")
        return

    summary = f"补全完成！\n\n"
    summary += f"脱敏行: {filled + kept}\n"
    summary += f"成功补全: {filled} 条\n"
    summary += f"保留原样: {kept} 条"
    if details:
        summary += "\n\n未补全明细:\n" + "\n".join(details)
    summary += f"\n\n文件已保存至: {save_path}"

    QMessageBox.information(self, "处理结果", summary)
