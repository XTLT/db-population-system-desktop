from .._imports import *
from .._consts import *
from ..funcs import *

PensionInsuranceImportWorker = None

class PensionInsuranceImportDialogOnFinishedMixin:
    def _on_finished(self, result):
        if result.get("dry_run"):
            if not confirm_precheck(self, result):
                self.lbl_status.setText("已取消导入")
                return
            self._run_import(False)
            return
        msg = f"导入完成！\n成功：{result.get('imported', 0)}条\n跳过：{result.get('skipped', 0)}条"
        if result.get("errors"):
            msg += f"\n错误：{len(result['errors'])}条\n" + "\n".join(result["errors"][:5])
        self.lbl_status.setText("导入完成")
        QMessageBox.information(self, "导入结果", msg)
        self.accept()
