import logging
from pathlib import Path


def validate_path(path_string):
    logger = logging.getLogger("configure_logger")

    path = Path(path_string)

    if not path.exists():
        logger.error("The path does not exist")
        return False

    return True
