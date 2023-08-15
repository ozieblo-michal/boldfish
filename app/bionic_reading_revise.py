import http.client
import constants
import logging


def bionic_reading_revise(
    definitions: dict, BIONIC_READING_X_RAPID_API_KEY: str
) -> dict:
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
