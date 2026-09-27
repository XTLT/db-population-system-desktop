import shutil


def _update_status_bar(self):
    if self.is_network_mode:
        self.lbl_backup.setText("备份状态：服务器管理")
        self.lbl_backup.setStyleSheet("color: #666;")
    else:
        from data.excel_importer import get_backup_status
        backup_info = get_backup_status()
        if backup_info["last_backup"]:
            self.lbl_backup.setText(f"最近备份：{backup_info['last_backup']}")
            self.lbl_backup.setStyleSheet("color: green;")
        else:
            self.lbl_backup.setText("备份状态：无备份")
            self.lbl_backup.setStyleSheet("color: orange;")
    
    total, used, free = shutil.disk_usage("/")
    free_gb = free // (1024**3)
    if free_gb < 10:
        self.lbl_disk.setText(f"磁盘空间：{free_gb}GB ⚠️")
        self.lbl_disk.setStyleSheet("color: red; font-weight: bold;")
    else:
        self.lbl_disk.setText(f"磁盘空间：{free_gb}GB")
        self.lbl_disk.setStyleSheet("color: green;")
