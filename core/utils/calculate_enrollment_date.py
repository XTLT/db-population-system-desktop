from datetime import date


def calculate_enrollment_date(grade: str, _birth_date_str: str = None) -> str:
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
