from PyQt6.QtWidgets import QMessageBox
from data.excel_importer import backup_database


def _manual_backup(self):
    if self.is_network_mode:
        reply = QMessageBox.question(
            self, "确认备份",
            "确定要备份服务器数据库吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from network.client import _request
                result = _request('POST', '/api/backup')
                if result.get('success'):
                    QMessageBox.information(self, "成功", "服务器数据库备份成功！")
                else:
                    QMessageBox.critical(self, "备份失败", result.get('error', '未知错误'))
            except Exception as e:
                QMessageBox.critical(self, "备份失败", str(e))
    else:
        path = backup_database()
        if path:
            QMessageBox.information(self, "成功", f"备份已保存到：{path}")
        else:
            QMessageBox.warning(self, "提示", "数据库文件不存在，无法备份")
