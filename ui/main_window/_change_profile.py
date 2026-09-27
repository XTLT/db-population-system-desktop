from PyQt6.QtWidgets import QMessageBox


def _change_profile(self):
    if not self.current_user:
        QMessageBox.warning(self, "提示", "未获取到用户信息！")
        return
    from dialogs.user_dialog import ChangeProfileDialog
    dialog = ChangeProfileDialog(self.current_user, self)
    if dialog.exec():
        pass
