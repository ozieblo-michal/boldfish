import http.client
import os
import random
import re
from io import StringIO
from pathlib import Path

import constants
import genanki
import openai
import pandas as pd
from bs4 import BeautifulSoup, Comment


class Boldfish:

    """
    Main package class.
    Contains two public methods:
        - get_definitions: to assign definitions to concepts (including an adapter for a CSV or JSON file path,
          a string with a single subject or multiple commas separated, or (to be done) for list input)
        - create_deck_of_flashcards: to create a deck of cards, optionally using Bionic Reading formatting on definitions
    """

    def __init__(
        self,
        OPENAI_API_KEY=None,
        BIONIC_READING_X_RAPID_API_KEY=None,
        model: str = "gpt-3.5-turbo",
    ):
        """Constructor:

        Args:
            OPENAI_API_KEY (str, optional): OpenAI API key. Defaults to None. openai.api_key value automatically by reading it from an environment variable
                                            named OPENAI_API_KEY. The OpenAI Python library is designed to check for this
                                            environment variable by default
            BIONIC_READING_X_RAPID_API_KEY (str, optional): API key to use Bionic Reading on definitions. Defaults to None.
            model (str, optional): large multimodal model by OpenAI. Defaults to "gpt-3.5-turbo". Recommended to switch to "gpt-4" (paid subscription)
        """
        self.OPENAI_API_KEY = OPENAI_API_KEY
        self.BIONIC_READING_X_RAPID_API_KEY = BIONIC_READING_X_RAPID_API_KEY
        self.model = model

    def __process_csv_data(self, path: str) -> str:
        """CSV input adapter

        Args:
            path (str): path to the CSV file

        Returns:
            str: comma-separated entities
        """
        content = pd.read_csv(path, header=None, comment=";").rename(
            columns={0: "concept"}
        )
        return ", ".join(content.concept.drop_duplicates().to_numpy().tolist())

    def __process_json_data(self, path: str) -> str:
        """JSON data adapter

        Args:
            path (str): path to the JSON file

        Returns:
            str: comma-separated entities
        """
        content = pd.read_json(path).rename(columns={0: "concept"})
        return ", ".join(content.concept.drop_duplicates().to_numpy().tolist())

    def __validate_path(self, path_string: str) -> bool:
        """Check if the string is a valid path

        Args:
            path_string (str): path to CSV or JSON file

        Returns:
            bool: Boolean answer
        """
        self.path_string = path_string

        path = Path(self.path_string)

        if not path.exists():  # raise error
            return False

        return True

    def __check_manually_entered_entities(self, user_input: str) -> bool:
        """Check if the input is comma-separated collection of entities

        Args:
            user_input (str): comma-separated collection of entities

        Returns:
            bool: Boolean answer
        """

        pattern = r"^(?!.*(--|\s\s))[A-Za-z0-9,\s-]+$"

        if "," in user_input:
            if len(user_input) >= 5:
                return re.match(pattern, user_input) is not None
        else:
            if len(user_input) >= 2:
                return re.match(pattern, user_input) is not None
        return False

    def __synthesize_entity_data(self, user_input: str) -> str:
        # old __get_entities
        """Combine entity data from different adapter methods. Perform check of the input.

        Args:
            user_input (str): path, comma-separated string of entities or TODO: list

        Raises:
            ValueError: invalid input

        Returns:
            str: comma-separated string of entities
        """
        self.user_input = user_input

        path = Path(self.user_input)

        if not self.__validate_path(path):
            if not self.__check_manually_entered_entities(self.user_input):
                raise ValueError

            return user_input

        if path.suffix != ".csv" and path.suffix != ".json":
            if path.suffix == ".csv":
                return self.__process_csv_data(self, path)

            if path.suffix == ".json":
                return self.__process_json_data(self, path)

    def __openai_answer(self, content: str) -> dict:
        """Call to OpenAI API to pass definitions to given entities

        Args:
            content (str): comma-separated string with one or multiple entities

        Returns:
            dict: concept:'definition' dictionary with definitions as plain text
        """

        """
        openai.api_key value automatically by reading it from an environment variable
        named OPENAI_API_KEY. The OpenAI Python library is designed to check for this
        environment variable by default
        """
        openai.api_key = self.OPENAI_API_KEY
        messages = [{"role": "system", "content": constants.TASK_DEFINITION}]

        if content:
            messages.append(
                {"role": "user", "content": content},
            )
            chat = openai.ChatCompletion.create(model=self.model, messages=messages)

        reply = chat.choices[0].message.content
        csvStringIO = StringIO(reply)
        df = pd.read_csv(csvStringIO, sep=";")

        return df.set_index("concept").to_dict()["definition"]

    def __bionic_reading_revise(self, definitions: dict) -> dict:
        """Uses the Bionic Reading API to format each definition text

        Args:
            definitions (dict): concept:'definition' dictionary with definitions as plain text

        Returns:
            dict: origin dictionary with values (definitions) overwritten in HyperText Markup Language
        """

        conn = http.client.HTTPSConnection(constants.BIONIC_READING_API_URL)

        bionic_reading_revised_definitions = {}

        headers = {
            "content-type": constants.BIONIC_READING_API_CONTENT_TYPE,
            "X-RapidAPI-Key": self.BIONIC_READING_X_RAPID_API_KEY,
            "X-RapidAPI-Host": constants.BIONIC_READING_X_RAPID_API_HOST,
        }

        # TODO: use a single request

        for key in definitions:
            payload = (
                f"content={definitions[key]}&response_type="
                "html&request_type=html&fixation=1&saccade=10"
            )
            conn.request("POST", "/convert", payload, headers)
            res = conn.getresponse()
            data = res.read()
            if key not in bionic_reading_revised_definitions.keys():
                bionic_reading_revised_definitions[key] = str(data.decode("utf-8"))

        return bionic_reading_revised_definitions

    def __create_deck_of_flashcards(
        self, definitions: dict, deck_name: str, output_directory: Path
    ) -> None:
        """Create deck of Anki flashcard in a giver directory.

        Raises:
            ValueError: if there is already a file with Anki deck for the given deck name and directory

        Returns:
            None: Creates an .apkg Anki deck file in a given directory
        """

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
            definition = definitions[key]

            soup = BeautifulSoup(definition, features="html5lib")
            div = soup.find(class_="bionic-reader-content")

            if div:
                for element in div(text=lambda text: isinstance(text, Comment)):
                    element.extract()
                note = genanki.Note(
                    model=model, fields=[key, re.sub(" +", " ", str(div))]
                )

            else:
                note = genanki.Note(model=model, fields=[key, definition])

            deck.add_note(note)

        filename = f"{deck_name}.apkg"
        pkg = genanki.Package(deck)

        if os.path.exists(f"{output_directory}/{filename}"):
            raise ValueError

        pkg.write_to_file(f"{output_directory}/{filename}")

        return None

    def get_definitions(self, entities: str) -> dict:
        """Format the entities using the appropriate adapter and provide
            a dictionary of definitions for the indicated terms using OpenAI API

        Args:
            entities (str): path, comma-separated string of entities or TODO: list

        Returns:
            dict: concept:'definition' dictionary with definitions as plain text
        """
        self.entities = entities
        entities = self.__synthesize_entity_data(
            self.entities
        )  # entities_adapter ?? ; add list adapter

        return self.__openai_answer(entities, self.OPENAI_API_KEY, self.model)

    def create_deck_of_flashcards(
        self, definitions: dict, deck_name: str, output_directory: Path
    ) -> None:
        """Create Anki deck with flashcards optionally using Bionic Reading formatting on definitions

        Args:
            definitions (dict): concept:'definition' dictionary with definitions as plain text
            deck_name (str): unique deck name
            output_directory (Path): directory

        Raises:
            ValueError: if the path doen not exists

        Returns:
            None: Creates an .apkg Anki deck file in a given directory
        """

        # TODO: definitons as class object

        if not self.__validate_path(output_directory):
            raise ValueError

        if self.BIONIC_READING_X_RAPID_API_KEY:
            definitions = self.__bionic_reading_revise(definitions)

        return self.__create_deck_of_flashcards(
            definitions, deck_name, output_directory
        )
