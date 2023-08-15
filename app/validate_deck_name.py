import re


def validate_deck_name(input_string: str) -> bool:
    pattern = r"^[A-Za-z]{3,}$"
    return re.match(pattern, input_string) is not None
