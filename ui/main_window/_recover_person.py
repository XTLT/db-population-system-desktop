


def _recover_person(self):
    from dialogs.person.recover_dialog import RecoverDialog
    dialog = RecoverDialog(self)
    if dialog.exec():
        self._refresh_status()
