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
