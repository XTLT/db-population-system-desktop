from dialogs.house_build import HouseBuildListDialog


def _view_house_build(self):
    dialog = HouseBuildListDialog(self.is_network_mode, self)
    dialog.exec()
