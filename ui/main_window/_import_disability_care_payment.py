from dialogs.disability_care_payment.import_dialog import DisabilityCareImportDialog


def _import_disability_care_payment(self):
    dialog = DisabilityCareImportDialog(self.is_network_mode, self)
    if dialog.exec():
        pass
