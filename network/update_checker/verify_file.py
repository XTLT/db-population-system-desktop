from .calculate_sha256 import calculate_sha256


def verify_file(filepath: str, expected_checksum: str) -> bool:
    if not expected_checksum or not expected_checksum.startswith("sha256:"):
        return True

    expected_hash = expected_checksum[7:]
    actual_hash = calculate_sha256(filepath)
    return expected_hash == actual_hash
