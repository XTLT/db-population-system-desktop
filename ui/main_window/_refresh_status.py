from core.database import get_person_count


def _refresh_status(self):
    if self.is_network_mode:
        try:
            from network.client import api_stats
            stats = api_stats()
            self.lbl_status.setText(f"数据库记录数：{stats.get('total_persons', '?')}")
        except Exception:
            self.lbl_status.setText("数据库记录数：获取失败")
    else:
        count = get_person_count()
        if count == 0:
            self.lbl_status.setText("记录数：0（空库，请导入或连接服务器）")
        else:
            self.lbl_status.setText(f"数据库记录数：{count}")
    self._update_status_bar()
