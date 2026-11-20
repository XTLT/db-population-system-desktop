from .._imports import *
from .._consts import *
from ..funcs import *

_HEADERS = None
_LOCAL_MODULES = None
_to_amount = None

class SubsidySummaryDialogRenderMixin:
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
                r.get("bank_account", ""),
                r.get("payment_status", ""),
                r.get("village", ""),
                r.get("fail_reason", "") or r.get("town", ""),
            ]
            for col_idx, val in enumerate(values):
                item = QTableWidgetItem(str(val) if val else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)
        self.table.setUpdatesEnabled(True)

        # 银行账号列宽度：按最长账号 + 左右留白，保证 19 位账号完整可见
        fm = self.table.fontMetrics()
        widest = max(
            [fm.horizontalAdvance(str(r.get("bank_account", "") or "")) for r in records] or [0]
        )
        want = max(fm.horizontalAdvance("银行账号"), widest) + 36
        self.table.setColumnWidth(3, want)
