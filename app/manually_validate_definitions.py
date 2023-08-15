import logging


def manually_validate_definitions(definitions: dict, max_num_of_attempts: int = 3):
    logger = logging.getLogger("configure_logger")

    definitions_to_be_repeated = []

    for key in list(definitions):
        logger.info("Confirm content...")
        logger.info("Concept: %s", key)
        logger.info("Definition: %s", definitions[key])

        num_of_attempts = 0

        while num_of_attempts < max_num_of_attempts:
            try:
                confirm = int(
                    input(
                        "The flashcard is okay (1)/not okay - reload definition (2)/not "
                        "okay - remove and forget about (3): "
                    )
                )
            except ValueError:
                num_of_attempts += 1
                logger.error("Invalid input - it must be integer")
                continue

            if confirm not in {1, 2, 3}:
                num_of_attempts += 1
                logger.error("Invalid value of input - it must be 1 or 2")
                continue

            if confirm == 1:
                break

            if confirm == 2:
                definitions_to_be_repeated.append(key)
                definitions.pop(key)
                break

            if confirm == 3:
                definitions.pop(key)
                break

            logger.error(
                "Content confirmation failed 3 times. The record is removed from the collection!"
            )

    return definitions, definitions_to_be_repeated
