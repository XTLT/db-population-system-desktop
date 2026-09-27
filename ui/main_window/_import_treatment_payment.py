from dialogs.treatment_payment.import_dialog import TreatmentPaymentImportDialog


def _import_treatment_payment(self):
    dialog = TreatmentPaymentImportDialog(self.is_network_mode, self)
    if dialog.exec():
        pass
