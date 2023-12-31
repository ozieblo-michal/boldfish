import http.client
import logging

import constants


def bionic_reading_revise(
    definitions: dict, BIONIC_READING_X_RAPID_API_KEY: str
) -> dict:
    """Uses the Bionic Reading API to format each definition text

    Args:
        definitions (dict): concepts and definitions given as a plain string
        BIONIC_READING_X_RAPID_API_KEY (str):
        from https://rapidapi.com/bionic-reading-bionic-reading-default/api/bionic-reading1

    Returns:
        dict: origin dictionary with values (definitions) overwritten in HyperText Markup Language
    """
    logger = logging.getLogger("configure_logger")

    conn = http.client.HTTPSConnection(constants.BIONIC_READING_API_URL)

    bionic_reading_revised_definitions = {}

    headers = {
        "content-type": constants.BIONIC_READING_API_CONTENT_TYPE,
        "X-RapidAPI-Key": BIONIC_READING_X_RAPID_API_KEY,
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

    logger.info("Bionic Reading applied")

    return bionic_reading_revised_definitions
