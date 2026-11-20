from .._imports import *
from .._consts import *
from ..funcs import *



class LandSubsidyViewDialogDoExportMixin:
    def _do_export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "导出地力补贴", f"地力补贴_{datetime.now().strftime('%Y%m%d')}.xlsx",
            "Excel文件 (*.xlsx)"
        )
        if not path:
            return

        import pandas as pd
        data = []
        headers = ["序号", "补贴年度", "户主姓名", "身份证号", "电话号码", "银行账号", "金融机构",
                   "发放金额", "上账时间", "耕地面积", "耕地标准", "油菜面积", "油菜标准", "油菜金额"]
        for row in range(self.table.rowCount()):
            row_data = {}
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data[headers[col]] = item.text() if item else ""
            data.append(row_data)
        df = pd.DataFrame(data)
        df.to_excel(path, index=False, engine="openpyxl")
        from data.excel_importer import _auto_fit_columns
        _auto_fit_columns(path)
        QMessageBox.information(self, "成功", f"数据已导出到：\n{path}")
