def safe_str(val) -> str:
    if val is None:
        return ""
    return str(val).strip()
