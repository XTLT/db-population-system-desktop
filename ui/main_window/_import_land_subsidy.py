from dialogs.land_subsidy.import_dialog import LandSubsidyImportDialog


def _import_land_subsidy(self):
    dialog = LandSubsidyImportDialog(self.is_network_mode, self)
    if dialog.exec():
        pass
