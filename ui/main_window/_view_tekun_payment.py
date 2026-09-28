from dialogs.tekun_payment.view_dialog import TekunViewDialog


def _view_tekun_payment(self):
    is_admin = self.current_user.get('role') == 'admin'
    dialog = TekunViewDialog(self.is_network_mode, is_admin, self)
    dialog.exec()
