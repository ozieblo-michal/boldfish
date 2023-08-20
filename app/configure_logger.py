import logging


def configure_logger(log_path: str) -> logging.Logger:
    """Configuration for the entire package, in order to print
    the content of logs to the console in the course of script
    processing and parallel writing them to a file
    in the indicated destination

    Args:
        log_path (str): output directory

    Returns:
        _type_: _description_
    """
    logger = logging.getLogger("configure_logger")

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
