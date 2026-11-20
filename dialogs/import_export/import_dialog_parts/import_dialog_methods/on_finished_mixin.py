from .._imports import *
from .._consts import *
from ..funcs import *

ImportWorker = None

class ImportDialogOnFinishedMixin:
    def _on_finished(self, result):
        msg = f"导入完成！\n成功：{result['imported']}条"
        if "updated" in result:
            msg += f"\n更新：{result['updated']}条"
        msg += f"\n跳过：{result['skipped']}条"
        if result["errors"]:
            msg += f"\n错误：{len(result['errors'])}条\n" + "\n".join(result["errors"][:5])
        self.lbl_status.setText("导入完成")
        QMessageBox.information(self, "导入结果", msg)
        self.accept()
