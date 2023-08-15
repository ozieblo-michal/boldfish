import os
import logging
from pathlib import Path

from validate_path import validate_path


def get_output_directory(max_num_of_attempts: int = 3) -> Path | str:
    logger = logging.getLogger("configure_logger")

    num_of_attempts = 0

    while num_of_attempts < max_num_of_attempts:
        current_working_directory = os.getcwd()

        logger.info(f"Current working directory: {current_working_directory}")

        path = Path(
            input(
                "Pass the output directory or skip (enter) to keep current working directory: "
            )
        )

        if path:
            if not validate_path(path):
                num_of_attempts += 1
                continue

        return path

    raise ValueError
