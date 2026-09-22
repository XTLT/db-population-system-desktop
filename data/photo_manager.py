import os
import shutil

from core.config import PHOTOS_DIR, PHOTO_EXTENSIONS
from core.utils import clean_filename, find_existing_photo, get_photo_base_name


def save_photo(source_path: str, photo_type: str, id_card: str, social1: str, social2: str, social3: str) -> bool:
    base_name = get_photo_base_name(photo_type, id_card, social1, social2, social3)
    if not base_name:
        return False
    cleaned = clean_filename(base_name)
    ext = os.path.splitext(source_path)[1].lower()
    if ext not in PHOTO_EXTENSIONS:
        return False
    dest = os.path.join(PHOTOS_DIR, cleaned + ext)
    old = find_existing_photo(base_name, PHOTOS_DIR)
    if old and old != dest and os.path.exists(old):
        os.remove(old)
    shutil.copy2(source_path, dest)
    return True


def delete_photo(photo_type: str, id_card: str, social1: str, social2: str, social3: str) -> bool:
    base_name = get_photo_base_name(photo_type, id_card, social1, social2, social3)
    if not base_name:
        return False
    path = find_existing_photo(base_name, PHOTOS_DIR)
    if path and os.path.exists(path):
        os.remove(path)
        return True
    return False


def get_photo_path(photo_type: str, id_card: str, social1: str, social2: str, social3: str) -> str:
    base_name = get_photo_base_name(photo_type, id_card, social1, social2, social3)
    if not base_name:
        return ""
    return find_existing_photo(base_name, PHOTOS_DIR)


def get_photo_status(id_card: str, social1: str, social2: str, social3: str) -> str:
    for card in [id_card, social1, social2, social3]:
        path = find_existing_photo(card, PHOTOS_DIR)
        if path:
            ext = os.path.splitext(path)[1].upper()
            return f"已有照片 ({ext[1:]})"
    return "暂无照片"


def export_photo(source_path: str, dest_path: str) -> bool:
    if os.path.exists(source_path):
        shutil.copy2(source_path, dest_path)
        return True
    return False


def open_photos_folder():
    os.startfile(PHOTOS_DIR) if os.name == "nt" else os.system(f'xdg-open "{PHOTOS_DIR}"')
