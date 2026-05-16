def get_eew(name: str) -> int:
    if name.endswith(("8.v", "8ff.v")):
        return 8
    if name.endswith(("16.v", "16ff.v")):
        return 16
    if name.endswith(("32.v", "32ff.v")):
        return 32
    return 0
