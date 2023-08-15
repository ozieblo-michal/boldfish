import os
import pandas as pd
import logging
import datetime
import sys

from get_output_directory import get_output_directory
from get_entities import get_entities
from openai_answer import openai_answer
from manually_validate_definitions import manually_validate_definitions
from bionic_reading_revise import bionic_reading_revise
from get_deck_name import get_deck_name
from create_deck_of_flashcards import create_deck_of_flashcards
from loading_animation import loading_animation
from configure_logger import configure_logger

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
BIONIC_READING_X_RAPID_API_KEY = os.environ.get("BIONIC_READING_X_RAPID_API_KEY")


class NoValidatedConceptsAfterTheFirstIteration(Exception):
    ...
    pass


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    logging.info("Write the flashcards for me!")
    logging.info("Welcome to CLI")

    output_directory = get_output_directory()

    timestamp = str(datetime.datetime.now())

    log_path = f"{output_directory}/{timestamp}.log"

    logger = configure_logger(log_path)

    deck_name = get_deck_name()

    entities = get_entities()

    loading_animation()

    definitions = openai_answer(entities, OPENAI_API_KEY)

    sys.stdout.write("\r" + " " * 20 + "\r")  # Clear the loading animation
    sys.stdout.flush()

    selected_definitions, definitions_to_be_repeated = manually_validate_definitions(
        definitions
    )

    while definitions_to_be_repeated:
        definitions_to_be_repeated.sort(key=str.lower)
        definitions_to_be_repeated = ", ".join(definitions_to_be_repeated)

        logger.warning(f"Reprocessed concepts: {definitions_to_be_repeated}")

        loading_animation()

        definitions_repeated = openai_answer(definitions_to_be_repeated, OPENAI_API_KEY)

        sys.stdout.write("\r" + " " * 20 + "\r")
        sys.stdout.flush()

        (
            definitions_repeated,
            definitions_to_be_repeated,
        ) = manually_validate_definitions(definitions_repeated)

        if selected_definitions and definitions_repeated:
            selected_definitions = {**selected_definitions, **definitions_repeated}

        if not selected_definitions and definitions_repeated:
            selected_definitions = definitions_repeated

    try:
        final_definitions = {**selected_definitions, **definitions_repeated}
    except NoValidatedConceptsAfterTheFirstIteration:
        final_definitions = selected_definitions

    if final_definitions:
        bionic_reading_revised_definitions = bionic_reading_revise(
            final_definitions, BIONIC_READING_X_RAPID_API_KEY
        )

        pd.DataFrame(
            list(final_definitions.items()), columns=["concept", "definition"]
        ).to_csv(f"{output_directory}/{deck_name}.csv", index=False, header=True)

        create_deck_of_flashcards(
            bionic_reading_revised_definitions, deck_name, output_directory
        )
    else:
        logger.error("No approved concepts")
