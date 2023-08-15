import re


def check_manually_entered_entities(user_input: str) -> bool:
    pattern = r"^(?!.*(--|\s\s))[A-Za-z0-9,\s-]+$"

    if "," in user_input:
        if len(user_input) >= 5:
            return re.match(pattern, user_input) is not None
    else:
        if len(user_input) >= 2:
            return re.match(pattern, user_input) is not None
    return False
