from dialogs.disability_care_payment.view_dialog import DisabilityCareViewDialog


def _view_disability_care_payment(self):
    is_admin = self.current_user.get('role') == 'admin'
    dialog = DisabilityCareViewDialog(self.is_network_mode, is_admin, self)
    dialog.exec()
