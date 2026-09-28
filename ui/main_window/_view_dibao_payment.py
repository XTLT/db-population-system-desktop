from dialogs.dibao_payment.view_dialog import DibaoViewDialog


def _view_dibao_payment(self):
    is_admin = self.current_user.get('role') == 'admin'
    dialog = DibaoViewDialog(self.is_network_mode, is_admin, self)
    dialog.exec()
