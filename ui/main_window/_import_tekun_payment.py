from dialogs.tekun_payment.import_dialog import TekunImportDialog


def _import_tekun_payment(self):
    dialog = TekunImportDialog(self.is_network_mode, self)
    if dialog.exec():
        pass
