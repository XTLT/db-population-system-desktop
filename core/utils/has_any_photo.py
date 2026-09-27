from .find_existing_photo import find_existing_photo


def has_any_photo(id_card: str, social1: str, social2: str, social3: str, photos_dir: str) -> bool:
    for card in [id_card, social1, social2, social3]:
        if find_existing_photo(card, photos_dir):
            return True
    return False
