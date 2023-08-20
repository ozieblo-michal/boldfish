import logging
from pathlib import Path

import pandas as pd
from check_manually_entered_entities import check_manually_entered_entities
from log_entities import log_entities
from validate_path import validate_path


def process_csv_data(path):
    content = pd.read_csv(path, header=None, comment=";").rename(columns={0: "concept"})
    output = ", ".join(content.concept.drop_duplicates().to_numpy().tolist())
    log_entities(output)
    return output


def process_json_data(path):
    content = pd.read_json(path).rename(columns={0: "concept"})
    output = ", ".join(content.concept.drop_duplicates().to_numpy().tolist())
    log_entities(output)
    return output


def get_entities(max_num_of_attempts: int = 3) -> str:
    logger = logging.getLogger("configure_logger")

    num_of_attempts = 0

    while num_of_attempts < max_num_of_attempts:
        try:
            question = (
                "Select the method of specifying entities to assign definitions to them "
                "- get from a file (1) \n"
                "or entering entities manually, separating them with commas (2). Please "
                "enter 1 or 2 as answer.\n"
            )
            answer = int(input(question))
        except ValueError:
            num_of_attempts += 1
            logger.error("Invalid input - it must be integer")
            continue

        if answer not in {1, 2}:
            num_of_attempts += 1
            logger.error("Invalid value of input - it must be 1 or 2")
            continue

        if answer == 1:
            path_input = input(
                "Pass the path to the file (only .csv or .json are available): "
            )
            path = Path(path_input)

            if not validate_path(path):
                num_of_attempts += 1
                continue

            if path.suffix != ".csv" and path.suffix != ".json":
                num_of_attempts += 1
                logger.error(
                    "Invalid type of input data - only CSV and JSON are allowed"
                )
                continue

            if path.suffix == ".csv":
                logger.info("A comma-separated values (CSV) input was recognized")
                return process_csv_data(path)

            if path.suffix == ".json":
                logger.info("A JavaScript Object Notation input was recognized")
                return process_json_data(path)

        if answer == 2:
            logger.info("Manual entry of the list of entities was selected")
            concepts = input("Concept(s) (single or separated by a comma): ")

            if not check_manually_entered_entities(concepts):
                num_of_attempts += 1
                logger.error("Invalid manual input")
                continue

            log_entities(concepts)

            return concepts

    raise ValueError
