from PyQt6.QtWidgets import QMessageBox


def _change_profile(self):
    if not self.current_user:
        QMessageBox.warning(self, "提示", "未获取到用户信息！")
        return
    # 防重入：WSLg/xcb 等环境下菜单触发信号可能连发两次，
    # 若对话框已打开则忽略后续触发，避免弹出两个相同窗口。
    if getattr(self, '_profile_dialog_open', False):
        return
    from dialogs.user_dialog import ChangeProfileDialog
    dialog = ChangeProfileDialog(self.current_user, self)
    self._profile_dialog_open = True
    try:
        dialog.exec()
    finally:
        self._profile_dialog_open = False
