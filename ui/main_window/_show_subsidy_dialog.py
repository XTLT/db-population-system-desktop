from PyQt6.QtWidgets import QDialog
from dialogs.land_subsidy.view_dialog import LandSubsidyViewDialog


def _show_subsidy_dialog(self, subsidy_key: str, id_card: str, name: str, is_admin: bool, parent_dialog: QDialog):
    if subsidy_key == "land_subsidy":
        dialog = LandSubsidyViewDialog(self.is_network_mode, is_admin, parent_dialog)
        dialog.filter_id_card = id_card
        dialog.txt_search.setText(name)
        dialog.exec()
