from datetime import date

import os

from core.config import PHOTO_EXTENSIONS


def calculate_age(id_card: str) -> str:
    id_card = id_card.strip()
    if len(id_card) != 18:
        return ""
    if not id_card[:17].isdigit():
        return ""
    last = id_card[17].upper()
    if not (last.isdigit() or last == "X"):
        return ""
    try:
        year = int(id_card[6:10])
        month = int(id_card[10:12])
        day = int(id_card[12:14])
        birth = date(year, month, day)
        today = date.today()
        age = today.year - birth.year
        if (today.month, today.day) < (birth.month, birth.day):
            age -= 1
        return str(age)
    except (ValueError, IndexError):
        return ""


def clean_filename(name: str) -> str:
    if not name:
        return ""
    result = []
    for ch in name:
        code = ord(ch)
        if (48 <= code <= 57) or (65 <= code <= 90) or (97 <= code <= 122) or code == 95 or (19968 <= code <= 40959):
            result.append(ch)
        else:
            result.append("_")
    return "".join(result)


def find_existing_photo(base_name: str, photos_dir: str) -> str:
    if not base_name or base_name == "无":
        return ""
    cleaned = clean_filename(base_name)
    for ext in PHOTO_EXTENSIONS:
        path = os.path.join(photos_dir, cleaned + ext)
        if os.path.exists(path):
            return path
    return ""


def has_any_photo(id_card: str, social1: str, social2: str, social3: str, photos_dir: str) -> bool:
    for card in [id_card, social1, social2, social3]:
        if find_existing_photo(card, photos_dir):
            return True
    return False


def get_photo_base_name(photo_type: str, id_card: str, social1: str, social2: str, social3: str) -> str:
    mapping = {
        "身份证": id_card,
        "社保卡1": social1,
        "社保卡2": social2,
        "社保卡3": social3,
    }
    return mapping.get(photo_type, "")


def safe_str(val) -> str:
    if val is None:
        return ""
    return str(val).strip()


def calculate_enrollment_date(grade: str, birth_date_str: str = None) -> str:
    today = date.today()
    current_year = today.year

    if grade == "GRADUATED":
        return ""

    grade_levels = {
        "T1": 0,
        "K1": 1, "K2": 2, "K3": 3,
        "G1": 4, "G2": 5, "G3": 6, "G4": 7, "G5": 8, "G6": 9,
        "G7": 10, "G8": 11, "G9": 12,
        "G10": 13, "G11": 14, "G12": 15,
        "V1": 13, "V2": 14, "V3": 15,
        "J1": 13, "J2": 14, "J3": 15,
        "C1": 16, "C2": 17, "C3": 18,
        "Z1": 16, "Z2": 17, "Z3": 18,
        "U1": 19, "U2": 20, "U3": 21, "U4": 22, "U5": 23,
        "M1": 24, "M2": 25, "M3": 26,
        "D1": 27, "D2": 28, "D3": 29, "D4": 30
    }

    start_levels = {
        "T": 0, "K": 1, "G": 4, "V": 13, "J": 13, "C": 16, "Z": 16, "U": 19, "M": 24, "D": 27
    }

    level = grade_levels.get(grade, 0)
    prefix = grade[0] if grade else "G"
    start_level = start_levels.get(prefix, 4)

    years_in_grade = level - start_level
    enrollment_year = current_year - years_in_grade

    if today.month < 9:
        enrollment_year -= 1

    return f"{enrollment_year}-09-01"
