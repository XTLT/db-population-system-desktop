from dialogs.pension_insurance.view_dialog import PensionInsuranceViewDialog


def _view_pension_insurance(self):
    is_admin = self.current_user.get('role') == 'admin'
    dialog = PensionInsuranceViewDialog(self.is_network_mode, is_admin, self)
    dialog.exec()
