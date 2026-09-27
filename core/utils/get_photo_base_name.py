def get_photo_base_name(photo_type: str, id_card: str, social1: str, social2: str, social3: str) -> str:
    mapping = {
        "身份证": id_card,
        "社保卡1": social1,
        "社保卡2": social2,
        "社保卡3": social3,
    }
    return mapping.get(photo_type, "")
