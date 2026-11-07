"""人员补贴汇总：一屏查看该人 6 个补贴模块的发放记录。"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from core.config import BTN_CANCEL_COLOR, FONT_NAME, FONT_SIZE

# 模块键 -> (展示名, 期间字段, 金额字段)
# 本地库里地力补贴的期间字段是 subsidy_year、金额字段是 total_amount，其余 5 个模块统一为 period / amount
_LOCAL_MODULES = (
    ("dibao_payment", "低保", "period", "amount"),
    ("elderly_allowance", "高龄补贴", "period", "amount"),
    ("land_subsidy", "地力补贴", "subsidy_year", "total_amount"),
    ("disability_care_payment", "残疾护理补贴", "period", "amount"),
    ("pension_insurance", "养老保险", "period", "amount"),
    ("tekun_payment", "特困供养", "period", "amount"),
)

_HEADERS = ["补贴类型", "期间", "金额（元）", "发放状态", "村", "备注"]


def _to_amount(value) -> float:
    try:
        return float(str(value or "").replace(",", "").strip())
    except (TypeError, ValueError):
        return 0.0


class SubsidySummaryDialog(QDialog):
    def __init__(self, is_network_mode: bool, id_card: str, name: str, parent=None):
        super().__init__(parent)
        self.is_network_mode = is_network_mode
        self.id_card = (id_card or "").strip()
        self.person_name = name or ""
        self.setWindowTitle(f"补贴情况 - {self.person_name}")
        self.setFixedSize(1000, 620)
        self._setup_ui()
        try:
            self._load()
        except Exception as e:
            QMessageBox.warning(self, "提示", f"加载补贴数据时出错：{e}")

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        title = QLabel(f"{self.person_name}　{self.id_card}")
        title.setFont(QFont(FONT_NAME, 13))
        layout.addWidget(title)

        self.lbl_summary = QLabel("正在加载…")
        self.lbl_summary.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.lbl_summary.setWordWrap(True)
        layout.addWidget(self.lbl_summary)

        self.table = QTableWidget()
        self.table.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table.setColumnCount(len(_HEADERS))
        self.table.setHorizontalHeaderLabels(_HEADERS)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_close = QPushButton("关闭")
        btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px;")
        btn_close.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

    def _load(self):
        if self.is_network_mode:
            records, by_module, total_count, truncated = self._fetch_remote()
        else:
            records, by_module, total_count, truncated = self._query_local()
        self._render(records, by_module, total_count, truncated)

    def _fetch_remote(self):
        from network.client import _request

        data = _request("GET", f"/api/person/{self.id_card}/subsidies")
        return (
            data.get("records", []),
            data.get("by_module", []),
            data.get("total_count", 0),
            bool(data.get("truncated", False)),
        )

    def _query_local(self):
        from core.database import (
            DibaoPayment,
            DisabilityCarePayment,
            ElderlyAllowance,
            LandSubsidy,
            PensionInsurance,
            TekunPayment,
            get_session,
        )

        model_map = {
            "dibao_payment": DibaoPayment,
            "elderly_allowance": ElderlyAllowance,
            "land_subsidy": LandSubsidy,
            "disability_care_payment": DisabilityCarePayment,
            "pension_insurance": PensionInsurance,
            "tekun_payment": TekunPayment,
        }

        records = []
        by_module = []
        session = get_session()
        try:
            for module, label, period_attr, amount_attr in _LOCAL_MODULES:
                model = model_map[module]
                rows = session.query(model).filter(model.id_card == self.id_card).all()
                total = 0.0
                for r in rows:
                    period = getattr(r, period_attr, "") or ""
                    amount = getattr(r, amount_attr, "") or ""
                    total += _to_amount(amount)
                    records.append({
                        "module": module,
                        "label": label,
                        "period": period,
                        "amount": amount,
                        "payment_status": getattr(r, "payment_status", "") or "",
                        "fail_reason": getattr(r, "fail_reason", "") or "",
                        "village": getattr(r, "village", "") or "",
                    })
                by_module.append({
                    "module": module,
                    "label": label,
                    "count": len(rows),
                    "total_amount": f"{total:.2f}" if total else "",
                })
        finally:
            session.close()

        records.sort(key=lambda x: (x["period"] or ""), reverse=True)
        return records, by_module, len(records), False

    def _render(self, records, by_module, total_count, truncated):
        parts = []
        for item in by_module:
            if item.get("count"):
                amount = item.get("total_amount") or "0.00"
                parts.append(f"{item.get('label', '')} {item.get('count')} 条（{amount} 元）")
        if total_count:
            text = f"共 {total_count} 条记录：" + "；".join(parts) if parts else f"共 {total_count} 条记录"
        else:
            text = "该人在 6 个补贴模块中均无发放记录"
        if truncated:
            text += "（记录过多，仅显示最近 300 条）"
        self.lbl_summary.setText(text)

        self.table.setUpdatesEnabled(False)
        self.table.setRowCount(len(records))
        for row_idx, r in enumerate(records):
            values = [
                r.get("label", ""),
                r.get("period", ""),
                r.get("amount", ""),
                r.get("payment_status", ""),
                r.get("village", ""),
                r.get("fail_reason", "") or r.get("town", ""),
            ]
            for col_idx, val in enumerate(values):
                item = QTableWidgetItem(str(val) if val else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)
        self.table.setUpdatesEnabled(True)
