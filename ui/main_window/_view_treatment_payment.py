from dialogs.treatment_payment.view_dialog import TreatmentPaymentViewDialog


def _view_treatment_payment(self):
    is_admin = self.current_user.get('role') == 'admin'
    dialog = TreatmentPaymentViewDialog(self.is_network_mode, is_admin, self)
    dialog.exec()
