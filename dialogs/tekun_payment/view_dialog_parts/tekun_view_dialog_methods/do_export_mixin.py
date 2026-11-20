from .._imports import *
from .._consts import *
from ..funcs import *



class TekunViewDialogDoExportMixin:
    def _do_export(self):
        try:
            period = self.txt_period.text().strip()
            id_card = self.txt_id_card.text().strip()

            if self.is_network_mode:
                from network.client import _request
                query = []
                if period:
                    query.append(('period', period))
                if id_card:
                    query.append(('id_card', id_card))
                path = '/api/tekun_payment'
                if query:
                    path += '?' + urlencode(query)
                data = _request('GET', path)
                records = data.get('records', []) or []
            else:
                from data.excel_importer import get_all_tekun_payments
                records = get_all_tekun_payments(period, id_card)

            if not records:
                QMessageBox.warning(self, "提示", "没有数据可导出")
                return

            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出Excel", f"特困_{datetime.now().strftime('%Y%m%d')}.xlsx",
                "Excel文件 (*.xlsx)"
            )
            if not file_path:
                return

            import pandas as pd
            data = []
            for p in records:
                if isinstance(p, dict):
                    data.append({
                        "费款所属期": p.get('period', ''),
                        "姓名": p.get('name', ''),
                        "身份证号": p.get('id_card', ''),
                        "所属乡镇": p.get('town', ''),
                        "所属村": p.get('village', ''),
                        "银行账号": p.get('bank_account', ''),
                        "金额": p.get('amount', ''),
                        "支付标志": p.get('payment_status', ''),
                        "导入来源": p.get('import_source', ''),
                    })
                else:
                    _id_card = getattr(p, 'id_card', '')
                    data.append({
                        "费款所属期": getattr(p, 'period', ''),
                        "姓名": p.name,
                        "身份证号": _id_card,
                        "所属乡镇": getattr(p, 'town', ''),
                        "所属村": getattr(p, 'village', ''),
                        "银行账号": p.bank_account,
                        "金额": p.amount,
                        "支付标志": getattr(p, 'payment_status', ''),
                        "导入来源": getattr(p, 'import_source', ''),
                    })

            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            from data.excel_importer import _auto_fit_columns
            _auto_fit_columns(file_path)
            QMessageBox.information(self, "提示", f"导出成功！\n共 {len(records)} 条记录")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败：{e}")
