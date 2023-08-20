import logging

from validate_deck_name import validate_deck_name


def get_deck_name(max_num_of_attempts: int = 3):
    logger = logging.getLogger("configure_logger")

    num_of_attempts = 0

    while num_of_attempts < max_num_of_attempts:
        deck_name = input("Pass the deck name: ")

        if not validate_deck_name(deck_name):
            num_of_attempts += 1
            logger.error(
                "The name must include only characters or is less that 3 characters long"
            )
            continue

        return deck_name

    raise ValueError
