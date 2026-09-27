from datetime import date


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
