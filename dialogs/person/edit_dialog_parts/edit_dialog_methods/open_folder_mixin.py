from .._imports import *
from .._consts import *
from ..funcs import *



class EditDialogOpenFolderMixin:
    def _open_folder(self):
        from data.photo_manager import open_photos_folder
        open_photos_folder()
