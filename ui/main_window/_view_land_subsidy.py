from dialogs.land_subsidy.view_dialog import LandSubsidyViewDialog


def _view_land_subsidy(self):
    is_admin = self.current_user.get('role') == 'admin'
    dialog = LandSubsidyViewDialog(self.is_network_mode, is_admin, self)
    dialog.exec()
