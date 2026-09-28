from dialogs.dibao_payment.import_dialog import DibaoImportDialog


def _import_dibao_payment(self):
    dialog = DibaoImportDialog(self.is_network_mode, self)
    if dialog.exec():
        pass
