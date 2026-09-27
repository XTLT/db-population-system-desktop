from dialogs.pension_insurance.import_dialog import PensionInsuranceImportDialog


def _import_pension_insurance(self):
    dialog = PensionInsuranceImportDialog(self.is_network_mode, self)
    if dialog.exec():
        pass
