from dialogs.elderly_allowance.view_dialog import ElderlyAllowanceViewDialog


def _view_elderly_allowance(self):
    is_admin = self.current_user.get('role') == 'admin'
    dialog = ElderlyAllowanceViewDialog(self.is_network_mode, is_admin, self)
    dialog.exec()
