import os

from core.config import PHOTOS_DIR


def open_photos_folder():
    os.startfile(PHOTOS_DIR) if os.name == "nt" else os.system(f'xdg-open "{PHOTOS_DIR}"')
