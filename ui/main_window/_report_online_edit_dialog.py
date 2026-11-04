"""本地在线编辑窗口：不依赖浏览器，用 desktop 内嵌 mTLS 客户端证书直连服务器。

替代原 webbrowser.open 方式（浏览器缺客户端证书会报 ERR_BAD_SSL_CLIENT_AUTH_CERT）。
数据流：
  GET  /api/reports/<id>/data   → {headers, rows}（Bearer token）
  POST /api/reports/<id>/save   → {success}（Bearer token）

编辑器能力（v0.0.39）：
  - 双击/按键编辑单元格
  - 批量插入行 / 删除行（多选）
  - 批量插入列 / 删除列（多选）
  - 撤销 / 重做（Ctrl+Z / Ctrl+Y，编辑与增删行列均可）
  - 查找 / 替换（当前表内）
  - 脏标记：有未保存修改时关闭会提示
"""
import copy

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QHeaderView, QAbstractItemView,
    QLineEdit, QGroupBox, QApplication,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
from core.config import FONT_NAME, BTN_ADD_COLOR, FONT_SIZE, BTN_CANCEL_COLOR

UNDO_LIMIT = 50


class ReportEditDialog(QDialog):
    """报表在线编辑对话框（本地表格编辑器，保存回服务器）"""

    def __init__(self, report_id: str, report_name: str, parent=None):
        super().__init__(parent)
        self.report_id = report_id
        self.report_name = report_name
        self._undo_stack = []      # 快照列表（每项 [headers, rows] 深拷贝）
        self._redo_stack = []
        self._modified = False
        self._suppress_change = False   # 内部填充/恢复时屏蔽 itemChanged
        self._last_find_row = -1        # 查找游标
        self.setWindowTitle(f"在线编辑 - {report_name}")
        self.resize(1100, 660)
        self._build_ui()
        self._bind_shortcuts()
        self._load_data()

    # ---------- UI ----------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # 工具栏
        toolbar = QHBoxLayout()
        for text, tip, slot in (
            ("插入行", "在选中行上方插入行（多选插入多行，无选中在末尾追加）", self._insert_rows),
            ("删除行", "删除选中的行（支持多行）", self._delete_rows),
            ("插入列", "在选中列左侧插入列（多选插入多列，无选中在末尾追加）", self._insert_cols),
            ("删除列", "删除选中的列（支持多列）", self._delete_cols),
            ("撤销", "撤销上一步操作 (Ctrl+Z)", self._undo),
            ("重做", "重做被撤销的操作 (Ctrl+Y)", self._redo),
        ):
            btn = QPushButton(text)
            btn.setToolTip(tip)
            btn.setStyleSheet("padding: 5px 14px;")
            btn.clicked.connect(slot)
            toolbar.addWidget(btn)
        toolbar.addStretch()

        self.btn_save = QPushButton("保存")
        self.btn_save.setStyleSheet(
            f"background-color: {BTN_ADD_COLOR}; color: white; font-weight: bold; padding: 5px 18px;"
        )
        self.btn_save.clicked.connect(self._save)
        toolbar.addWidget(self.btn_save)
        btn_close = QPushButton("关闭")
        btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 5px 14px;")
        btn_close.clicked.connect(self.reject)
        toolbar.addWidget(btn_close)
        layout.addLayout(toolbar)

        # 查找/替换栏
        findbox = QGroupBox("查找 / 替换")
        fh = QHBoxLayout(findbox)
        fh.setContentsMargins(8, 4, 8, 4)
        fh.addWidget(QLabel("查找："))
        self.ed_find = QLineEdit()
        self.ed_find.setPlaceholderText("输入要查找的内容")
        self.ed_find.setFixedWidth(220)
        self.ed_find.returnPressed.connect(self._find_next)
        fh.addWidget(self.ed_find)
        btn_find_next = QPushButton("查找下一个")
        btn_find_next.clicked.connect(self._find_next)
        fh.addWidget(btn_find_next)
        fh.addSpacing(12)
        fh.addWidget(QLabel("替换为："))
        self.ed_replace = QLineEdit()
        self.ed_replace.setPlaceholderText("替换后的内容")
        self.ed_replace.setFixedWidth(220)
        fh.addWidget(self.ed_replace)
        btn_replace = QPushButton("替换")
        btn_replace.clicked.connect(self._replace_once)
        fh.addWidget(btn_replace)
        btn_replace_all = QPushButton("全部替换")
        btn_replace_all.clicked.connect(self._replace_all)
        fh.addWidget(btn_replace_all)
        fh.addStretch()
        layout.addWidget(findbox)

        # 表格
        self.table = QTableWidget()
        self.table.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
            | QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.table, 1)

        # 状态栏
        self.lbl_status = QLabel("正在加载报表数据...")
        self.lbl_status.setStyleSheet("color: #666; font-size: 13px; padding: 4px 0;")
        layout.addWidget(self.lbl_status)

    def _bind_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Z"), self, activated=self._undo)
        QShortcut(QKeySequence("Ctrl+Y"), self, activated=self._redo)
        QShortcut(QKeySequence("Ctrl+F"), self, activated=lambda: self.ed_find.setFocus())

    # ---------- 数据加载 ----------
    def _load_data(self):
        try:
            from network.client import _request
            data = _request('GET', f'/api/reports/{self.report_id}/data')
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取报表数据失败：{e}")
            self.reject()
            return
        headers = data.get('headers', []) or []
        rows = data.get('rows', []) or []
        if not headers:
            headers = [''] * max((len(r) for r in rows), default=0)
        self._suppress_change = True
        try:
            self._fill_table(headers, rows)
        finally:
            self._suppress_change = False
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._modified = False
        self.lbl_status.setText(
            f"已加载 {len(rows)} 行 × {len(headers)} 列（双击编辑；可增删行列/撤销重做/查找替换，完成后点保存）"
        )

    def _fill_table(self, headers, rows):
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                self.table.setItem(r, c, item)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setDefaultSectionSize(28)

    # ---------- 快照（撤销/重做） ----------
    def _snapshot(self):
        headers = []
        for c in range(self.table.columnCount()):
            hi = self.table.horizontalHeaderItem(c)
            headers.append(hi.text() if hi else '')
        rows = []
        for r in range(self.table.rowCount()):
            row = []
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                row.append(item.text() if item else '')
            rows.append(row)
        return [headers, rows]

    def _push_undo(self):
        snap = copy.deepcopy(self._snapshot())
        self._undo_stack.append(snap)
        if len(self._undo_stack) > UNDO_LIMIT:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def _restore_snapshot(self, snap):
        headers, rows = snap
        self._suppress_change = True
        try:
            self._fill_table(headers, rows)
        finally:
            self._suppress_change = False
        self._mark_modified()

    def _undo(self):
        if not self._undo_stack:
            self.lbl_status.setText("没有可撤销的操作")
            return
        self._redo_stack.append(copy.deepcopy(self._snapshot()))
        snap = self._undo_stack.pop()
        self._restore_snapshot(snap)
        self.lbl_status.setText("已撤销")

    def _redo(self):
        if not self._redo_stack:
            self.lbl_status.setText("没有可重做的操作")
            return
        self._undo_stack.append(copy.deepcopy(self._snapshot()))
        snap = self._redo_stack.pop()
        self._restore_snapshot(snap)
        self.lbl_status.setText("已重做")

    # ---------- 增删行列（批量） ----------
    def _selected_rows(self):
        """当前选中区域涉及的行号集合（去重升序）"""
        rows = set()
        for idx in self.table.selectionModel().selectedRows():
            rows.add(idx.row())
        for idx in self.table.selectionModel().selectedIndexes():
            rows.add(idx.row())
        return sorted(rows)

    def _selected_cols(self):
        cols = set()
        for idx in self.table.selectionModel().selectedColumns():
            cols.add(idx.column())
        for idx in self.table.selectionModel().selectedIndexes():
            cols.add(idx.column())
        return sorted(cols)

    def _insert_rows(self):
        self._push_undo()
        sel = self._selected_rows()
        n = len(sel) if sel else 1
        anchor = sel[0] if sel else self.table.rowCount()   # 无选中 → 末尾追加
        self.table.insertRow(anchor)
        for _ in range(n - 1):
            self.table.insertRow(anchor)
        self._mark_modified()
        self.lbl_status.setText(f"已插入 {n} 行")

    def _delete_rows(self):
        sel = self._selected_rows()
        if not sel:
            QMessageBox.information(self, "提示", "请先选中要删除的行")
            return
        if QMessageBox.question(self, "确认", f"确定删除选中的 {len(sel)} 行？此操作可撤销。") \
                != QMessageBox.StandardButton.Yes:
            return
        self._push_undo()
        for r in reversed(sel):
            self.table.removeRow(r)
        self._mark_modified()
        self.lbl_status.setText(f"已删除 {len(sel)} 行")

    def _insert_cols(self):
        self._push_undo()
        sel = self._selected_cols()
        n = len(sel) if sel else 1
        anchor = sel[0] if sel else self.table.columnCount()
        self.table.insertColumn(anchor)
        for _ in range(n - 1):
            self.table.insertColumn(anchor)
        self._mark_modified()
        self.lbl_status.setText(f"已插入 {n} 列")

    def _delete_cols(self):
        sel = self._selected_cols()
        if not sel:
            QMessageBox.information(self, "提示", "请先选中要删除的列")
            return
        if QMessageBox.question(self, "确认", f"确定删除选中的 {len(sel)} 列？此操作可撤销。") \
                != QMessageBox.StandardButton.Yes:
            return
        self._push_undo()
        for c in reversed(sel):
            self.table.removeColumn(c)
        self._mark_modified()
        self.lbl_status.setText(f"已删除 {len(sel)} 列")

    # ---------- 编辑/脏标记 ----------
    def _on_item_changed(self, _item):
        if self._suppress_change:
            return
        # 单元格编辑提交时入撤销栈（编辑期间不去抖：QTableWidget 在编辑提交时才发一次）
        self._push_undo()
        self._mark_modified()

    def _mark_modified(self):
        self._modified = True
        self.btn_save.setStyleSheet(
            f"background-color: #E67E22; color: white; font-weight: bold; padding: 5px 18px;"
        )

    # ---------- 查找/替换 ----------
    def _find_all_items(self, keyword):
        return self.table.findItems(keyword, Qt.MatchFlag.MatchContains)

    def _find_next(self):
        keyword = self.ed_find.text()
        if not keyword:
            return
        items = self._find_all_items(keyword)
        if not items:
            self.lbl_status.setText(f"未找到「{keyword}」")
            self._last_find_row = -1
            return
        # 从上次位置之后循环
        start = self._last_find_row + 1
        target = None
        for it in items:
            if it.row() >= start:
                target = it
                break
        if target is None:
            target = items[0]
        self.table.setCurrentCell(target.row(), target.column())
        self.table.setFocus()
        self._last_find_row = target.row()
        self.lbl_status.setText(f"找到第 {target.row() + 1} 行第 {target.column() + 1} 列")

    def _replace_once(self):
        keyword = self.ed_find.text()
        repl = self.ed_replace.text()
        if not keyword:
            return
        self._find_next()
        idx = self.table.currentIndex()
        if idx.isValid():
            item = self.table.item(idx.row(), idx.column())
            if item and keyword in item.text():
                self._push_undo()
                self._suppress_change = True
                try:
                    item.setText(item.text().replace(keyword, repl, 1))
                finally:
                    self._suppress_change = False
                self._mark_modified()
                self.lbl_status.setText("已替换 1 处")

    def _replace_all(self):
        keyword = self.ed_find.text()
        repl = self.ed_replace.text()
        if not keyword:
            return
        items = self._find_all_items(keyword)
        if not items:
            self.lbl_status.setText(f"未找到「{keyword}」")
            return
        if QMessageBox.question(self, "确认", f"确定将全部 {len(items)} 处「{keyword}」替换为「{repl}」？此操作可撤销。") \
                != QMessageBox.StandardButton.Yes:
            return
        self._push_undo()
        self._suppress_change = True
        try:
            for it in items:
                it.setText(it.text().replace(keyword, repl))
        finally:
            self._suppress_change = False
        self._mark_modified()
        self.lbl_status.setText(f"已替换 {len(items)} 处")

    # ---------- 保存 ----------
    def _collect_data(self):
        """收集表头与全部单元格数据（与服务器保存接口约定一致）"""
        headers = []
        for c in range(self.table.columnCount()):
            header_item = self.table.horizontalHeaderItem(c)
            headers.append(header_item.text() if header_item else '')

        rows = []
        for r in range(self.table.rowCount()):
            row = []
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                row.append(item.text() if item else '')
            rows.append(row)
        return headers, rows

    def _save(self):
        headers, rows = self._collect_data()
        if not headers or all(h == '' for h in headers):
            QMessageBox.warning(self, "提示", "报表没有表头，无法保存")
            return
        self.btn_save.setEnabled(False)
        self.lbl_status.setText("正在保存...")
        try:
            from network.client import _request
            _request('POST', f'/api/reports/{self.report_id}/save',
                     data={'headers': headers, 'rows': rows})
        except Exception as e:
            self.btn_save.setEnabled(True)
            self.lbl_status.setText("保存失败")
            QMessageBox.critical(self, "错误", f"保存失败：{e}")
            return
        self.btn_save.setEnabled(True)
        self.btn_save.setStyleSheet(
            f"background-color: {BTN_ADD_COLOR}; color: white; font-weight: bold; padding: 5px 18px;"
        )
        self._modified = False
        self.lbl_status.setText(f"保存成功（{len(rows)} 行 × {len(headers)} 列）")
        QMessageBox.information(self, "提示", f"保存成功（{len(rows)} 行 × {len(headers)} 列）")

    # ---------- 关闭拦截 ----------
    def reject(self):
        if self._modified:
            ret = QMessageBox.question(
                self, "未保存修改",
                "报表有未保存的修改，关闭将丢失这些修改。\n\n确定要关闭吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if ret != QMessageBox.StandardButton.Yes:
                return
        super().reject()
