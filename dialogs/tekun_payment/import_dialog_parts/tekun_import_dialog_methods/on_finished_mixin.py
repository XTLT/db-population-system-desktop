from .._imports import *
from .._consts import *
from ..funcs import *

TekunImportWorker = None

class TekunImportDialogOnFinishedMixin:
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
        not_found = result.get("not_found", [])
        if not_found:
            unique_not_found = list(set(not_found))
            msg += f"\n\n数据库中未找到的人员（{len(unique_not_found)}人）：\n"
            msg += "\n".join(unique_not_found[:20])
            if len(unique_not_found) > 20:
                msg += f"\n...等{len(unique_not_found)}人"
        self.lbl_status.setText("导入完成")
        QMessageBox.information(self, "导入结果", msg)
        self.accept()
