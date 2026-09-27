import os

from core.config import PHOTO_EXTENSIONS
from .clean_filename import clean_filename


def find_existing_photo(base_name: str, photos_dir: str) -> str:
    if not base_name or base_name == "无":
        return ""
    cleaned = clean_filename(base_name)
    for ext in PHOTO_EXTENSIONS:
        path = os.path.join(photos_dir, cleaned + ext)
        if os.path.exists(path):
            return path
    return ""
