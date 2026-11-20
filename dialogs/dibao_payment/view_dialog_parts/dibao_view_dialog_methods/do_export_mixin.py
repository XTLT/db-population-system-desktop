from .._imports import *
from .._consts import *
from ..funcs import *



class DibaoViewDialogDoExportMixin:
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
                path = '/api/dibao_payment'
                if query:
                    path += '?' + urlencode(query)
                data = _request('GET', path)
                records = data.get('records', []) or []
            else:
                from data.excel_importer import get_all_dibao_payments
                records = get_all_dibao_payments(period, id_card)

            if not records:
                QMessageBox.warning(self, "提示", "没有数据可导出")
                return

            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出Excel", f"低保_{datetime.now().strftime('%Y%m%d')}.xlsx",
                "Excel文件 (*.xlsx)"
            )
            if not file_path:
                return

            import pandas as pd
            data = []
            for p in records:
                if isinstance(p, dict):
                    data.append({
                        "村名称": p.get('village', ''),
                        "救助类型": "低保",
                        "人员姓名": p.get('name', ''),
                        "人员身份证号": p.get('id_card', ''),
                        "性别": p.get('gender', ''),
                        "和申请人关系": p.get('relation', ''),
                        "共同生活家庭成员": p.get('family_members', ''),
                        "享受保障人口数": p.get('family_count', ''),
                        "家庭保障总金额": p.get('amount', ''),
                        "家庭最低生活基本保障金": p.get('base_amount', ''),
                        "家庭特殊困难补助金": p.get('special_amount', ''),
                        "家庭调剂金额": p.get('adjust_amount', ''),
                        "特殊困难情形（分类施保）": p.get('special_situation', ''),
                        "特殊困难补助金": p.get('special_subsidy', ''),
                        "初始享受时间": p.get('start_time', ''),
                        "始发年月": p.get('issue_month', '') or p.get('period', ''),
                        "费款所属期": p.get('period', ''),
                        "导入来源": p.get('import_source', ''),
                        "银行账号": p.get('bank_account', ''),
                    })
                else:
                    data.append({
                        "村名称": getattr(p, 'village', ''),
                        "救助类型": "低保",
                        "人员姓名": p.name,
                        "人员身份证号": getattr(p, 'id_card', ''),
                        "性别": getattr(p, 'gender', ''),
                        "和申请人关系": getattr(p, 'relation', ''),
                        "共同生活家庭成员": getattr(p, 'family_members', ''),
                        "享受保障人口数": getattr(p, 'family_count', ''),
                        "家庭保障总金额": p.amount,
                        "家庭最低生活基本保障金": getattr(p, 'base_amount', ''),
                        "家庭特殊困难补助金": getattr(p, 'special_amount', ''),
                        "家庭调剂金额": getattr(p, 'adjust_amount', ''),
                        "特殊困难情形（分类施保）": getattr(p, 'special_situation', ''),
                        "特殊困难补助金": getattr(p, 'special_subsidy', ''),
                        "初始享受时间": getattr(p, 'start_time', ''),
                        "始发年月": getattr(p, 'issue_month', '') or getattr(p, 'period', ''),
                        "费款所属期": getattr(p, 'period', ''),
                        "导入来源": getattr(p, 'import_source', ''),
                        "银行账号": getattr(p, 'bank_account', ''),
                    })

            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            from data.excel_importer import _auto_fit_columns
            _auto_fit_columns(file_path)
            QMessageBox.information(self, "提示", f"导出成功！\n共 {len(records)} 条记录")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败：{e}")
