from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogOnPhotoTypeChangedMixin:
    def _on_photo_type_changed(self, text):
        self._load_current_photo()
