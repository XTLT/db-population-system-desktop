from dialogs.elderly_allowance.import_dialog import ElderlyAllowanceImportDialog


def _import_elderly_allowance(self):
    dialog = ElderlyAllowanceImportDialog(self.is_network_mode, self)
    if dialog.exec():
        pass
