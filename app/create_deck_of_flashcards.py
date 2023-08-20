import logging
import os
import random
import re
from pathlib import Path

import genanki
from bs4 import BeautifulSoup, Comment
from get_deck_name import get_deck_name


def create_deck_of_flashcards(
    definitions: dict, deck_name: str, output_directory: Path
) -> None:
    logger = logging.getLogger("configure_logger")

    while True:
        deck_id = random.randint(1000000000, 9999999999)
        model_id = random.randint(1000000000, 9999999999)

        model = genanki.Model(
            model_id,
            "TNFM",
            fields=[
                {"name": "Concept"},
                {"name": "Description"},
            ],
            templates=[
                {
                    "name": "Card 1",
                    "qfmt": "{{Concept}}",
                    "afmt": "{{Description}}",
                },
            ],
        )

        deck = genanki.Deck(deck_id, deck_name)

        for key in definitions:
            soup = BeautifulSoup(definitions[key], features="html5lib")
            div = soup.find(class_="bionic-reader-content")
            for element in div(text=lambda text: isinstance(text, Comment)):
                element.extract()
            note = genanki.Note(model=model, fields=[key, re.sub(" +", " ", str(div))])
            deck.add_note(note)

        filename = f"{deck_name}.apkg"
        pkg = genanki.Package(deck)

        if os.path.exists(f"{output_directory}/{filename}"):
            logger.error(
                "There is already a deck with that name in this directory, rename it"
            )
            deck_name = get_deck_name()
            continue

        pkg.write_to_file(f"{output_directory}/{filename}")

        logger.info(f"Deck named {filename} has been saved")

        break
